import re
import ansible
import random
import copy
import os
import common
import time
import cert


class UnsupportEtcdClientCmd(Exception):

    """Unsupport type of cmd for Etcd client"""

    def __init__(self, cmd):
        self.cmd = cmd

    def __str__(self):
        return "Unsupport command '%s' for Etcd client" % self.cmd


class UnsupportEtcdClientOption(Exception):

    """Unsupport options for Etcd client"""

    def __init__(self, cmd, option):
        self.cmd = cmd
        self.option = option

    def __str__(self):
        return "Command '%s' does not support option '%s'" % (self.cmd,
                                                              self.option)


class MissingFlags(Exception):

    """Flags missing in etcd conf or command help output"""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class UnSupportFlags(Exception):

    """Unsupport flags in etcd server"""

    def __init__(self, flag):
        self.flag = flag

    def __str__(self):
        return "Flag %s is not supported by etcd" % self.flag


class EtcdClientCmd(object):

    """
    This class help generate etcd client cmd for etcdctl or curl.
    """

    def __init__(self, etcdctl_supported=None):
        self.version = "v2"
        self.support_cmd_type = ["etcdctl", "curl"]
        self.peers = ["127.0.0.1:2379"]
        self.check_peer = self.peers[0]
        self.current_cmd_type = None
        self.output_format = None

        self.support_query_params = {"query_dir": False,
                                     "wait": False,
                                     "recursive": False,
                                     "sorted": False,
                                     "query_prevExist": False,
                                     "waitIndex": 0,
                                     "prevIndex": 0,
                                     "prevValue": ""}
        self.support_values = {"value": "",
                               "dir": False,
                               "ttl": 0,
                               "json": {},
                               "file": ""}
        self.support_auth_keys = ["key-file", "cert-file", "ca-file",
                                  "username"]
        self.support_category = ["stats", "keys", "members", "auths",
                                 "version"]
        etcdctl_users_trans = {"cmd": "user",
                               "check_keyword": "op",
                               "delete": "remove",
                               "get": {"check_keyword": "key",
                                       "": "list",
                                       ".*": "get"},
                               "put": {"check_keyword": "kargs",
                                       "json": {"check_keyword": "json",
                                                "grant": "grant",
                                                "revoke": "revoke",
                                                "": "add"},
                                       "prevExist=true": "passwd"}
                               }
        etcdctl_roles_trans = {"cmd": "role",
                               "check_keyword": "op",
                               "delete": "remove",
                               "get": {"check_keyword": "key",
                                       "": "list",
                                       ".*": "get"},
                               "put": {"check_keyword": "json",
                                       "grant": "grant",
                                       "revoke": "revoke",
                                       "": "add"},
                               }

        etcdctl_keys_put_trans = {"check_keyword": "kargs",
                                  "dir=True": {"prevExist=False": "mkdir",
                                               "prevExist=True": "updatedir",
                                               "": "setdir"},
                                  "": {"prevExist=False": "mk",
                                       "prevExist=True": "update",
                                       "": "set"}
                                  }
        etcdctl_keys_trans = {"get": {"check_keyword": "kargs",
                                      "dir=True": "ls",
                                      "wait=True": "watch",
                                      "": "get"},
                              "put": etcdctl_keys_put_trans,
                              "delete": {"check_keyword": "kargs",
                                         "dir=True": "rmdir",
                                         "": "rm"},
                              "check_keyword": "op"}

        self.etcdctl_option_trans = {"prevValue": {"set": "swap_with_value",
                                                   "rm": "with_value"},
                                     "prevIndex": {"set": "swap_with_index",
                                                   "rm": "with_index"}}

        self.etcdctl_cmd_trans = {"members": {"get": "list",
                                              "put": "add",
                                              "delete": "remove",
                                              "check_keyword": "op",
                                              "cmd": "member"},
                                  "auth": {"enable": {"put": "enable",
                                                      "delete": "disable",
                                                      "cmd": "auth",
                                                      "check_keyword": "op"},
                                           "users": etcdctl_users_trans,
                                           "roles": etcdctl_roles_trans,
                                           "check_keyword": "key"},
                                  "keys": etcdctl_keys_trans
                                  }

        self.etcdctl_supported = etcdctl_supported

    def get_cmd(self, cmd_type="curl", op="get", category="version", key=None,
                check_peer=None, full_cmd=False, **kargs):
        """
        Generate etcd client command based on the options given.

        :param cmd_type: Etcd client command, should be one of
                         curl and etcdctl
        :type cmd_type: str
        :param op: REST style operations, should be on of get, put,
                   delete and post
        :type op: str
        :param category: Etcd category for key store
        :type category: str
        :param key: The key stored in etcd
        :type key: str
        :param check_peer: machine address in cluster
        :type check_peer: str
        :param full_cmd: Add default options to curl command line or not
        :type full_cmd: bool
        :param kargs: Key word args for etcd client command
        :return: The whole command line for etcd client
        :rtype: str
        """
        if cmd_type == "random":
            cmd_type = random.choice(self.support_cmd_type)

        if cmd_type not in self.support_cmd_type:
            raise UnsupportEtcdClientCmd(cmd_type)

        if cmd_type == "etcdctl" and self.etcdctl_supported is None:
            raise UnsupportEtcdClientCmd("etcdctl")

        self.current_cmd_type = cmd_type
        if cmd_type == "curl":
            self.output_format = "json"
        else:
            self.output_format = "simple"

        func = getattr(self, "%s_update_params" % cmd_type)

        func(op=op, category=category, key_value=key, check_peer=check_peer,
             full_cmd=full_cmd, **kargs)

        func = getattr(self, "%s_cmd" % cmd_type)

        return func()

    def curl_update_params(self, op="get", category="version", key_value=None,
                           check_peer="127.0.0.1:2379", full_cmd=False,
                           **kargs):
        """
        Update parameters for curl command line based on the input.

        :param op: REST style operations, should be on of get, put,
                   delete and post
        :type op: str
        :param category: Etcd category for key store
        :type category: str
        :param key_value: The key stored in etcd
        :type key_value: str
        :param check_peer: machine address in cluster
        :type check_peer: str
        :param full_cmd: Add default options to curl command line or not
        :type full_cmd: bool
        :param kargs: Key word args for etcd client command
        """
        if category not in self.support_category:
            raise UnsupportEtcdClientOption("curl", category)

        if not check_peer:
            check_peer = self.check_peer

        self.op = op
        self.category = category
        self.key = key_value
        self.peers = check_peer

        self.protocol = "http"
        if full_cmd:
            self.etcd_query_params = self.support_query_params
            self.etcd_values = self.support_values
        else:
            self.etcd_query_params = {}
            self.etcd_values = {}
        self.auth_values = {}

        for key, value in kargs.items():
            if key in self.support_query_params:
                self.etcd_query_params[re.sub("query_", "", key)] = value
            elif key in self.support_values:
                self.etcd_values[key] = value
            elif key in self.support_auth_keys:
                if key == "username":
                    self.auth_values["-u"] = value
                else:
                    self.protocol = "https"
                    key = re.sub("-file", "", key)
                    if key == "ca":
                        key = "cacert"
                    self.auth_values["--%s" % key] = value
            else:
                raise UnsupportEtcdClientOption("curl", key)

    def curl_cmd(self):
        """
        Generate curl command line based on the options set.

        :return: The whole command line for etcd client
        :rtype: str
        """
        cmd = "curl"
        cmd += " -X %s" % self.op.upper()
        for key, value in self.auth_values.items():
            cmd += " %s \"%s\"" % (re.sub("-file", "", key), value)

        cmd += " -L \"%s://%s" % (self.protocol, self.peers.split(",")[0])
        if self.category == "version":
            cmd += "/version\""
            return cmd

        cmd += "/%s/%s/%s" % (self.version, self.category, self.key)

        query_params = "?"
        for key, value in self.etcd_query_params.items():
            query_params += "%s=%s&" % (key, value)

        query_params = query_params.rstrip("&")

        if query_params != "?":
            cmd += query_params

        cmd += "\""

        for key, value in self.etcd_values.items():
            if key == "file":
                cmd += " --data-urlencode \"value@%s\"" % value
            elif key == "json":
                cmd += " -H \"context-Type:application/json\" -d '%s'" % value
            else:
                cmd += " -d \"%s=%s\"" % (key, value)

        return cmd

    def _cmd_trans_base_dict(self, trans_dict, op, key_value,
                            check_method=None, **kargs):
        """
        Use translate dict and given parameters to get the etcdctl command

        :param trans_dict: The translate dict which stores the judgement key
                           word and key word categories for next step check.
        :type trans_dict: dict
        :param op: REST style operations, should be on of get, put,
                   delete and post
        :type op: str
        :param key_value: The key stored in etcd
        :type key_value: str
        :param check_method: The type of the keyword for the translate
        :type check_method: str
        :param kargs: The key value args for the command genrate
        """
        tmp_dict = None
        tmp_key = key_value
        tmp_kargs = kargs
        cmd = ""

        if "check_keyword" in trans_dict:
            check_method = trans_dict["check_keyword"]

        if check_method == "op":
            tmp_dict = trans_dict[op]
        elif check_method == "key":
            tmp_dict = key_value.strip("/").split("/")[0]
            tmp_key = "/".join(key_value.strip("/").split("/")[1:])
        elif check_method == "kargs":
            for key in trans_dict:
                if key == "check_keyword":
                    continue
                if key == "" and tmp_dict is None:
                    tmp_dict = trans_dict[key]
                elif key.split("=")[0] in kargs:
                    arg = key.split("=")[0]
                    if "%s=%s" % (arg, kargs[arg]) == key:
                        tmp_dict = trans_dict[key]
                        tmp_kargs.pop(arg)
                        break
        elif check_method == "json":
            check_dict = kargs["json"]
            for key in trans_dict:
                if key == "" and tmp_dict is None:
                    tmp_dict = trans_dict[key]
                elif key in check_dict:
                    tmp_dict = trans_dict[key]
                    break

        if "cmd" in trans_dict:
            cmd += " %s" % trans_dict["cmd"]
        if isinstance(tmp_dict, dict):
            tmp = self._cmd_trans_base_dict(tmp_dict, op, tmp_key,
                                            check_method, **kargs)
            tmp_key = tmp[1]
            tmp_kargs = tmp[2]
            cmd += " %s" % tmp[0]
        else:
            cmd += " %s" % tmp_dict

        if cmd is not None:
            cmd = cmd.strip()

        if tmp_key is not None:
            tmp_key = tmp_key.strip()

        return cmd, tmp_key, tmp_kargs

    def etcdctl_update_params(self, op="get", category="version",
                              key_value=None, check_peer=None, full_cmd=False,
                              **kargs):
        """
        Update parameters for etcdctl command line based on the input.

        :param cmd_type: Etcd client command, should be one of
                         curl and etcdctl
        :type cmd_type: str
        :param op: REST style operations, should be on of get, put,
                   delete and post
        :type op: str
        :param category: Etcd category for key store
        :type category: str
        :param key_value: The key stored in etcd
        :type key_value: str
        :param check_peer: machine address in cluster
        :type check_peer: str
        :param full_cmd: Add default options to curl command line or not
        :type full_cmd: bool
        :param kargs: Key word args for etcd client command
        """

        if (category not in self.support_category
                and category not in self.etcdctl_supported["commands"]):
            raise UnsupportEtcdClientOption("", category)

        self.global_options = {}
        self.cmd_options = {}
        self.args = {}
        self.cmd = None
        self.sub_cmd = None
        left_key = ""

        tmp = {}
        for key, value in kargs.items():
            tmp_key = re.sub("query_", "", key)
            tmp[tmp_key] = value

        kargs = tmp

        if check_peer:
            self.global_options["peers"] = check_peer

        if category == "version":
            self.global_options["version"] = None
            self.cmd = ""
        elif category not in self.etcdctl_cmd_trans:
            self.cmd = category
            self.sub_cmd = key_value
        else:
            cmd_trans = self.etcdctl_cmd_trans[category]
            _ = self._cmd_trans_base_dict(cmd_trans, op,
                                          key_value,
                                          check_method=None,
                                          **kargs)
            self.cmd, left_key, kargs = _

            if len(self.cmd.split()) > 1:
                self.sub_cmd = self.cmd.split()[1]
                self.cmd = self.cmd.split()[0]

        for key, value in kargs.items():
            if key in self.etcdctl_option_trans:
                key = self.etcdctl_option_trans[key]
            if key in self.etcdctl_supported["global_options"]:
                self.global_options[key] = value
            elif (key
                  in self.etcdctl_supported["commands"][self.cmd]["options"]):
                self.cmd_options[key] = value
            elif key == "value":
                self.args[left_key] = value
            else:
                self.args[key] = value

        if category == "keys" and left_key not in self.args:
            self.args[left_key] = ""

    def etcdctl_cmd(self):
        """
        Generate etcdctl command line based on the options set.

        :return: The whole command line for etcd client
        :rtype: str
        """
        cmd = "etcdctl"

        if "output" in self.global_options:
            self.output_format = self.global_options["output"]

        for key, value in self.global_options.items():
            cmd += " --%s" % key
            if value is not None:
                cmd += " %s" % value

        cmd += " %s" % self.cmd
        if self.sub_cmd:
            cmd += " %s" % self.sub_cmd

        for key, value in self.cmd_options.items():
            cmd += " --%s" % key
            if value is not None:
                cmd += " %s" % value
        for key, value in self.args.items():
            cmd += " %s" % key
            if value is not None:
                cmd += " %s" % value

        return cmd


class EtcdServer(object):

    """
    This class help generate the etcd.conf context or etcd command line.
    """

    def __init__(self, server_type, default_conf=None, etcd_help=None):
        self.cmd_only = ['version', 'h', 'help']
        self.server_type = server_type
        self.default_conf = default_conf
        self.etcd_help = etcd_help
        self.flags = {}

    def set_flag(self, flag, value):
        """
        Set one flag with the given value

        :param flag: Flag of the etcd server
        :type flag: str
        :param value: Value set to the flag
        :type value: str
        """
        if flag not in self.supported_flags:
            raise UnSupportFlags(flag)

        self.flags[flag] = value

    def unset_flag(self, flag):
        """
        Remove one flag from the etcd server config

        :param flag: Flag of the etcd server
        :type flag: str
        """
        if flag in self.flags:
            self.flags.pop(flag)

    def guess_type(self, text):
        """
        Check and return the method to start the etcd server

        :param text: The output of help or context of conf file
        :type text: str
        :return: The method to start etcd server.
        :rtype: str
        """
        if "ETCD_" in text:
            return "service"
        elif "usage:" in text:
            return "etcd"
        else:
            return "unknown"

    def get_supported_flags(self, text):
        """
        Get the supported flags of current version of etcd server based
        on the default conf file or commnad line help output.

        :param text: The output of help or context of conf file
        :type text: str
        :return: A categoried dict for supported flags
        :rtype: dict
        """
        income_type = self.guess_type(text)
        supported_flags = {}
        category = ""
        if income_type == "service":
            category_pattern = r"\[(\w+)]"
            flag_pattern = r'ETCD_([A-Z_]+)=(.*)$'
            option_name = "unset"
            option_pattern = r"^#ETCD_"
        elif income_type == "etcd":
            category_pattern = r"^(\w+)\sflags"
            flag_pattern = r"^\s+-+([\w-]+)\s+'(.*)'|^\s+-+([\w-]+)\s+(\d+)"
            flag_pattern += r"|^\s+-+([\w-]+)"
            option_name = "deprecated"
            option_pattern = r"\[DEPRECATED\]"

        for line in text.splitlines():
            if re.findall(category_pattern, line):
                if category:
                    supported_flags[category] = tmp
                category = re.findall(category_pattern, line)[0]
                category = re.sub("ing$", "", category)
                tmp = {}
            else:
                if not re.findall(flag_pattern, line):
                    continue
                flag_t = re.findall(flag_pattern, line)[0]
                flag_t = [_ for _ in flag_t if _]
                if len(flag_t) > 1:
                    flag = flag_t[0]
                    value = flag_t[1]
                else:
                    flag = flag_t[0]
                    value = ""
                flag = re.sub("_", "-", flag).lower()
                tmp[flag] = {"default_value": value}
                if re.search(option_pattern, line):
                    tmp[flag]["option"] = option_name
        supported_flags[category] = tmp

        return supported_flags

    def get_flag_list(self, supported_flags):
        """
        Get all supported flags from supported flags dict

        :param supported_flags: categoried supported flags
        :type supported_flags: dict
        :return: a list of supported flags
        :rtype: list
        """
        tmp_list = []
        for category in supported_flags:
            tmp_list += supported_flags[category]
        return tmp_list

    def check_flags(self):
        """
        Check the uniformity of the conf file and command line help output
        """
        if self.default_conf is None or self.etcd_help is None:
            return

        wrong_category = []
        conf_miss = []
        etcd_miss = []

        conf_flags = self.get_supported_flags(self.default_conf)
        etcd_flags = self.get_supported_flags(self.etcd_help)
        conf_list = self.get_flag_list(conf_flags)
        etcd_miss = copy.copy(conf_list)

        for category in etcd_flags:
            if category in ["unsafe", "experimental"]:
                continue
            check_all = False
            if category not in conf_flags:
                check_all = True
                check_flags = etcd_flags[category].keys()
            else:
                for flag in etcd_flags[category]:
                    the_flag = etcd_flags[category][flag]
                    if ("option" in the_flag
                            and the_flag["option"] == "deprecated"):
                        continue
                    if flag not in conf_flags[category]:
                        check_all = True
                        check_flags = [flag]
                    else:
                        etcd_miss.remove(flag)
            if check_all:
                for flag in check_flags:
                    if flag in conf_list:
                        wrong_category.append(flag)
                        etcd_miss.remove(flag)
                    else:
                        conf_miss.append(flag)

        err_msg = ""
        if wrong_category:
            err_msg += "Following flags are in wrong "
            err_msg += "category: '%s'\n" % " ".join(wrong_category)
        if conf_miss:
            err_msg += "Following flags are missing in "
            err_msg += "etcd.conf: '%s'\n" % " ".join(conf_miss)
        if etcd_miss:
            err_msg += "Following flags are missing in "
            err_msg += "etcd help: '%s'\n" % " ".join(etcd_miss)

        if err_msg:
            raise MissingFlags(err_msg)


class EtcdServerConf(EtcdServer):

    """Etcd service conf file for testing"""

    def __init__(self, default_conf=None, etcd_help=None):
        super(EtcdServerConf, self).__init__("service", default_conf,
                                             etcd_help)
        supported_flags = self.get_supported_flags(self.default_conf)
        self.supported_flags = self.get_flag_list(supported_flags)

    def get(self):
        """
        Generate the context of the conf file

        :return: The conf file context
        :rtype: str
        """
        text = "#[fromtest]\n"
        for flag in self.flags:
            txt = self.flags[flag]
            text += "ETCD_%s=\"%s\"\n" % (re.sub("-", "_", flag).upper(),
                                          self.flags[flag])

        return text


class EtcdServerCmd(EtcdServer):

    """Etcd command line for testing"""

    def __init__(self, default_conf=None, etcd_help=None):
        super(EtcdServerCmd, self).__init__("etcd", default_conf, etcd_help)
        self.supported_flags = self.cmd_only
        supported_flags = self.get_supported_flags(self.etcd_help)
        self.supported_flags += self.get_flag_list(supported_flags)

    def get(self):
        """
        Generate the etcd command line

        :return: Etcd command line
        :rtype: str
        """
        cmd = "etcd"
        for flag in self.flags:
            cmd += " --%s %s" % (flag, self.flags[flag])
        return cmd


def get_sections(help_text):
    """
    Get the flags sections from help output

    :param help_text: Output from help
    :type help_text: str
    :return: etcd flags sections
    :rtype: dict
    """
    etcd_items = {}
    for line in help_text.splitlines():
        if re.match("[\s\w]+:$", line):
            name = re.findall("[\s\w]+", line)[0].lower()
            etcd_items[name] = ""
        elif line:
            etcd_items[name] += "%s\n" % line

    return etcd_items


def get_items(text):
    """
    Get items from each section of help output

    :param text: section text
    :type text: str
    :return: the items in the section
    :rtype: list
    """
    return [re.split("\s|,", _.strip(" -"))[0] for _ in text.splitlines()]


def etcdctl_help(context, host):
    """
    Get the text from etcdctl help
    """
    result = context.remote_cmd("command", host, module_args="etcdctl help")
    return result[0]["stdout"]


def etcdctl_cmd_help(context, cmd, host):
    """
    Get the help text from etcdctl sub command
    """
    result = context.remote_cmd("command", host,
                                module_args="etcdctl %s --help" % cmd)
    return result[0]["stdout"]


def etcd_help(context, host):
    """
    Get the text from etcd --help
    """
    result = context.remote_cmd("command", host, module_args="etcd --help")

    return result[0]["stdout"]

def etcdctl_get_support_cmds(context, host):
    """
    Get etcdctl supported command and options
    """
    help_dict = get_sections(etcdctl_help(context, host))
    cmds = get_items(help_dict["commands"])
    global_options = get_items(help_dict["global options"])

    etcdctl_supported = {}

    etcdctl_supported["global_options"] = global_options
    cmds_tmp = {}
    for cmd in cmds:
        cmds_tmp[cmd] = {}
        cmd_help = get_sections(etcdctl_cmd_help(context, cmd, host))
        if "commands" in cmd_help:
            cmds_tmp[cmd]["commands"] = get_items(cmd_help["commands"])
        if "options" in cmd_help:
            cmds_tmp[cmd]["options"] = get_items(cmd_help["options"])

    etcdctl_supported["commands"] = cmds_tmp

    return etcdctl_supported


@given(u'get etcd.conf context from "{host}"')
def step_impl(context, host):
    fetch_args = "dest=/var/tmp/etcd_default src=%s" % context.etcd_conf_file
    results = context.remote_cmd("fetch", host,
                                 module_args=fetch_args)

    file_path = results[0]["dest"]

    etcd_conf = open(file_path, "r")
    context.default_etcd_conf = etcd_conf.read()
    etcd_conf.close()


@then(u'set etcd.conf to "{path}" in "{host}"')
def step_impl(context, host, path):
    group_hosts = context.get_hosts()
    host_ips = group_hosts[host]
    hosts = []
    if len(host_ips) > 1:
        for host_ip in host_ips:
            for group in group_hosts:
                if group == host:
                    continue
                if group_hosts[group] == [host_ip]:
                    hosts.append((host_ip, group))
                    break
            else:
                assert False, "Can not find a host in ansible"
    else:
        hosts = [(host_ips[0], host)]

    for host_ip, host in hosts:
        copy_args = "dest=%s" % context.etcd_conf_file
        copy_args += " src=%s/%s" % (path, host_ip)
        copy_args += "/%s" % context.etcd_conf_file
        results = context.remote_cmd("copy", host, module_args=copy_args)
        assert 'failed' not in results[0], "Failed to copy etcd.conf"


@given(u'copy "{src}" to "{des}" in "{host}"')
def step_impl(context, src, des, host):
    if not os.path.isabs(src):
        src = os.path.join(context.src_dir, src)
    if not os.path.isabs(des):
        src = os.path.join(context.src_dir, des)
    copy_args = "dest=%s src=%s" % (des, src)
    results = context.remote_cmd("copy", host, module_args=copy_args)
    assert 'failed' not in results[0]


@given(u'restore etcd.conf context to "{host}"')
@then(u'restore etcd.conf context to "{host}"')
def step_impl(context, host):
    context.execute_steps(u"""
       Then set etcd.conf to "{path}" in "{host}"
        """.format(path="/var/tmp/etcd_default", host=host))


@then(u'set etcd.conf to "{host}"')
def step_impl(context, host):
    context.execute_steps(u"""
       Then set etcd.conf to "{path}" in "{host}"
        """.format(path="/var/tmp/etcd_update", host=host))


@given(u'get etcd help')
def step_impl(context):
    context.etcd_help = etcd_help(context, context.target_host)


@then(u'Compare etcd flags from help output and etcd.conf')
def step_impl(context):
    etcd_server = EtcdServer("compare", context.default_etcd_conf,
                             context.etcd_help)
    etcd_server.check_flags()


@then(u'init etcd client on "{host}"')
def step_impl(context, host):
    etcdctl_support = etcdctl_get_support_cmds(context, host)
    context.etcd_client_cmd = EtcdClientCmd(etcdctl_support)


@given(u'"{op}" etcd "{category}" "{key}" on "{host}" with "{args}"')
@then(u'"{op}" etcd "{category}" "{key}" on "{host}" with "{args}"')
def step_impl(context, op, category, key, host, args):
    check_peer = None
    full_cmd = False
    kargs = {}
    if args != "None":
        for arg in args.split():
            tmp_key, value = arg.split("=")
            if tmp_key == "check_peer":
                check_peer = value
            elif tmp_key == "full_cmd":
                full_cmd = value in ["True", "true"]
            elif value != "None":
                if value in ["False", "True"]:
                    value = eval(value)
                kargs[tmp_key] = value

    if key == "None":
        key = None

    cmd = context.etcd_client_cmd.get_cmd(context.etcdclient_type, op=op,
                                          category=category, key=key,
                                          check_peer=check_peer,
                                          full_cmd=full_cmd, **kargs)
    results = context.remote_cmd("command", host, module_args=cmd,
                                 ignore_rc=True)

    context.etcd_client_results = results

    if category == "keys":
        cmd_type = context.etcd_client_cmd.current_cmd_type
        kargs = {}
        if args != "None":
            for arg in args.split():
                tmp_key, value = arg.split("=")
                if (tmp_key in context.etcd_client_cmd.support_auth_keys
                        or tmp_key == "dir"):
                    kargs[tmp_key] = value

        if cmd_type == "etcdctl":
            output_format = context.etcd_client_cmd.output_format
            cmd = context.etcd_client_cmd.get_cmd(cmd_type,
                                                  "get", "keys", key=key,
                                                  check_peer=check_peer,
                                                  output=output_format,
                                                  **kargs)
        else:
            cmd = context.etcd_client_cmd.get_cmd(cmd_type,
                                                  "get", "keys", key=key,
                                                  check_peer=check_peer,
                                                  **kargs)

        context.etcd_key_check_cmd = cmd


@then(u'get etcd version on "{host}"')
def step_impl(context, host):
    context.execute_steps(u"""Given "get" etcd "version" "None" on "{host}" with "None"
                           """.format(host=host))


@then(u'"{value}" stored in etcd named "{key}" on "{host}"')
def step_impl(context, value, key, host):
    if not hasattr(context, "etcd_key_check_cmd"):
        return

    results = context.remote_cmd("command", host, ignore_rc=True,
                                 module_args=context.etcd_key_check_cmd)

    assert results

    if value == "None":
        emsg = "Key is still stored in server"
        for result in results:
            assert "Key not found" in str(result), emsg
    else:
        if value == '""':
            value = ""
        cmd_type = context.etcd_client_cmd.current_cmd_type
        output_format = context.etcd_client_cmd.output_format
        if "dir=true" in context.etcd_key_check_cmd.lower():
            value = eval(value)
            check_item = "dir"
        else:
            check_item = "value"
        for result in results:
            if output_format == "json":
                output = re.sub("true", "True", result["stdout"])
                output = re.sub("false", "False", output)
                rvalue = eval(output)["node"][check_item]
            elif output_format == "extend":
                rvalue = result["stdout"].splitlines()[-1]
            elif output_format == "simple":
                rvalue = result["stdout"]

            emsg = "'%s' value is %s but expect is %s" % (key, rvalue, value)
            assert rvalue == value, emsg


@then(u'check etcd keys on "{host}" in "{timeout}"s')
def step_impl(context, host, timeout):
    results = context.remote_cmd("command", host,
                                 module_args=context.etcd_key_check_cmd)

    assert results

    time.sleep(int(timeout))
    results = context.remote_cmd("command", host, ignore_rc=True,
                                 module_args=context.etcd_key_check_cmd)
    emsg = "Key is still stored in server after %ss" % timeout
    for result in results:
        assert "Key not found" in str(result), emsg


@given(u'"{action}" etcd key "{key}" on "{host}" expect "{value}"')
def step_impl(context, action, key, host, value):

    kargs = {}
    if action == "exec-watch":
        kargs["--"] = "sh -c \"echo %s &> /var/tmp/watch-output\"" % value

    cmd = context.etcd_client_cmd.get_cmd("etcdctl", op="get",
                                          category=action, key=key, **kargs)
    results = context.remote_cmd("command", host, module_args=cmd,
                                 ignore_rc=True, async=True)

    context.etcd_watch = results


@then(u'check etcd watch output is "{value}" and "{status}" on "{host}"')
def step_impl(context, value, status, host):
    results = context.etcd_watch.poll()

    if status == "finished":
        item = "contacted"
        finished = 1
        emsg = "Process not finished"
    else:
        item = "polled"
        finished = 0
        emsg = "Process is not running"
        context.remote_cmd("command", host,
                           module_args="cat /var/tmp/watch-output")
        values = context.result

    for host in results[item]:
        assert results[item][host]["finished"] == finished, emsg
        if finished:
            assert value == results[item][host]['stdout']
        else:
            assert value == values['contacted'][host]['stdout']


@then(u'set etcd key "{key}" with "{value}" on "{host}" for "{count}" times')
def step_impl(context, key, value, host, count):
    key_value = "value=%s" % value
    for loop in range(int(count)):
        context.execute_steps(u"""
          Given "put" etcd "keys" "{key}" on "{host}" with "{key_value}"
           Then check etcd watch output is "{value}" and "{status}" on "{host}"
                  """.format(key=key, host=host, key_value=key_value,
                             value=value, status="not finished"))

        time.sleep(1)


@given(u'a set of etcd cluster members')
def step_impl(context):
    context.etcd_cluster = {}
    host_groups = context.get_hosts()
    context.etcd_discovery_uuid = common.gen_uuid()
    if context.etcd_server_type == "service":
        etcd_server = EtcdServerConf
    elif context.etcd_server_type == "etcd":
        etcd_server = EtcdServerCmd
    else:
        emsg = "Can't start etcd service by %s" % context.etcd_server_type
        assert False, emsg

    for row in context.table:
        tmp = etcd_server(context.default_etcd_conf, context.etcd_help)
        for key, value in row.items():
            if value == "None":
                continue
            if key == "host":
                group_name = row["host"]
                host_ip = host_groups[group_name][0]
                continue
            if "uuid" in value:
                value = re.sub("uuid", context.etcd_discovery_uuid, value)
            if re.findall("_name|_ip", value):
                group_name = re.findall("([\w\-\_\*]+)_ip|([\w\-\_\*]+)_name",
                                        value)[0]
                group_name = group_name[0] or group_name[1]
                hosts = []
                if "*" in group_name:
                    group_names = [_ for _ in host_groups
                                   if re.findall(group_name, _)]
                    for gn in group_names:
                        hosts += host_groups[gn]
                else:
                    hosts = host_groups[group_name]
                re_group_name = re.sub("\*", "\\*", group_name)
                txt = []
                for host in hosts:
                    value_tmp = re.sub("%s_ip" % re_group_name, host, value)
                    if group_name == "all" or "*" in group_name:
                        real_gn = common.get_group_name(host_groups, host)
                        value_tmp = re.sub("%s_name" % re_group_name,
                                           real_gn,
                                           value_tmp)
                    else:
                        value_tmp = re.sub("%s_name" % re_group_name,
                                           group_name,
                                           value_tmp)
                    txt.append(value_tmp)
                value = ",".join(txt)
            tmp.set_flag(key, value)
        context.etcd_cluster[group_name] = [tmp, host_ip]


@then(u'start a proxy server on "{host}"')
def step_impl(context, host):
    host_groups = context.get_hosts()
    if context.etcd_server_type == "service":
        etcd_server = EtcdServerConf
    elif context.etcd_server_type == "etcd":
        etcd_server = EtcdServerCmd
    else:
        emsg = "Can't start etcd service by %s" % context.etcd_server_type
        assert False, emsg

    proxy_server = etcd_server(context.default_etcd_conf, context.etcd_help)
    proxy_server.set_flag("name", "proxy")
    proxy_server.set_flag("proxy", "on")
    proxy_server.set_flag("listen-client-urls",
                          "http://0.0.0.0:2379,http://0.0.0.0:4001")
    etcd_cluster_members = context.etcd_cluster
    member = etcd_cluster_members.values()[0][0]
    if "discovery" in member.flags:
        proxy_server.set_flag("discovery", member.flags["discovery"])
    elif "initial-cluster" in member.flags:
        proxy_server.set_flag("initial-cluster",
                              member.flags["initial-cluster"])

    context.etcd_cluster = {"proxy": [proxy_server, host_groups[host]]}
    context.execute_steps(u'Then start the etcd cluster')
    context.etcd_cluster = etcd_cluster_members


@given(u'create discovery url')
def step_impl(context):
    host_groups = context.get_hosts()
    if context.etcd_server_type == "service":
        etcd_server = EtcdServerConf
    elif context.etcd_server_type == "etcd":
        etcd_server = EtcdServerCmd
    else:
        emsg = "Can't start etcd service by %s" % context.etcd_server_type
        assert False, emsg
    discovery_server = etcd_server(context.default_etcd_conf,
                                   context.etcd_help)
    discovery_server.set_flag("name", "server")
    discovery_server.set_flag("data-dir", "/root/server.etcd")
    discovery_server.set_flag("listen-client-urls",
                              "http://0.0.0.0:2379,http://0.0.0.0:4001")
    discovery_server.set_flag("advertise-client-urls",
                              "http://0.0.0.0:2379,http://0.0.0.0:4001")
    discovery_server.set_flag("initial-cluster-state", "new")
    tmp = context.etcd_cluster
    context.etcd_cluster = {"server": [discovery_server,
                                       host_groups["server"]]}
    context.execute_steps(u'Then start the etcd cluster')
    context.etcd_cluster = tmp

    key = "/discovery/%s/_config/size" % context.etcd_discovery_uuid
    context.execute_steps(u"""
         Given "put" etcd "keys" "{key}" on "server" with "{value}"
         """.format(key=key,
                    value="value=%s" % str(len(context.etcd_cluster))))


@then(u'start the etcd cluster')
def step_impl(context):
    context.etcd_cluster_poller = []
    for host in context.etcd_cluster:
        server, host_ip = context.etcd_cluster[host]
        if "data-dir" in server.flags:
            data_dir = server.flags["data-dir"]
        elif context.etcd_server_type == "service":
            data_dir = "/var/lib/etcd/default.etcd"
            common.exec_service_cmd(context, "stop", "etcd", host)
        else:
            data_dir = "/var/tmp/%s.etcd" % server.flags["name"]

        context.remote_cmd("command", host, module_args="pkill etcd")

        context.remote_cmd("file", host,
                           module_args="state=absent path=%s" % data_dir)

        if context.etcd_server_type == "service":
            conf = server.get()
            file_path = "/var/tmp/etcd_update/%s/%s" % (host_ip,
                                                        context.etcd_conf_file)
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))

            conf_file = open(file_path, "w")
            conf_file.write(conf)
            conf_file.close()

            context.execute_steps(u"""
               Then set etcd.conf to "{host}"
                                """.format(host=host))
            context.etcd_conf_updated = True
            common.exec_service_cmd(context, "restart", "etcd", host)
            time.sleep(10)
        else:
            cmd = server.get()
            print("etcd start cmd is %s host is %s" % (cmd, host))
            args = "%s chdir=/var/tmp" % cmd
            results = context.remote_cmd("command", host, async=True,
                                         module_args=args)
            time.sleep(10)
            context.etcd_cluster_poller.append(results)


@then(u'check etcd cluster members')
def step_impl(context):
    context.execute_steps(u"""
       Given "{op}" etcd "{category}" "{key}" on "{host}" with "{args}"
       """.format(op="get", category="members", key="None", host="infra*",
                  args="None"))

    ids = []
    cmd_type = context.etcd_client_cmd.current_cmd_type
    for result in context.etcd_client_results:
        tmp = []
        if cmd_type == "service":
            for item in result["stdout"]["members"]:
                tmp.append(item["id"])
        else:
            tmp = re.findall("^(\w+)", result["stdout"], re.M)
        if ids:
            assert ids == tmp, "members get from etcd nodes are different"
        else:
            ids = tmp

        emsg = "cluster member number is wrong,"
        emsg += " expect is %s " % len(context.etcd_cluster)
        emsg += "but exist is %s and they are %s" % (len(ids), ids)
        assert len(context.etcd_cluster) == len(ids), emsg
        context.etcd_cluster_members = ids


@then(u'check etcd cluster health')
def step_impl(context):
    context.etcdclient_type = "etcdctl"
    context.execute_steps(u"""
       Given "{op}" etcd "{category}" "{key}" on "{host}" with "{args}"
       """.format(op="get", category="cluster-health", key="None",
                  host="infra*", args="None"))

    for result in context.etcd_client_results:
        output = result["stdout"]
        assert "cluster is healthy" in output, "Cluster is not healthy"

        if hasattr(context, "etcd_cluster_members"):
            for member in context.etcd_cluster_members:
                emsg = "Member %s is not healthy" % member
                assert "member %s is healthy" % member, emsg


@then(u'stop etcd server and clean up data-dir in host')
def step_imp(context):
    context.remote_cmd("command", "all", module_args="pkill -9 etcd")
    for host in context.etcd_cluster:
        server, host_ip = context.etcd_cluster[host]

        if "data-dir" in server.flags:
            data_dir = server.flags["data-dir"]
        else:
            cmd = "find / -name '%s.etcd'" % server.flags["name"]
            results = context.remote_cmd("command", host, module_args=cmd)
            data_dir = results[0]["stdout"]

        context.remote_cmd("file", host,
                           module_args="state=absent path=%s" % data_dir)


@given(u'generate "{filenames}" key pair for "{ips}"')
def step_imp(context, filenames, ips):
    path = context.src_dir
    ca_fn = os.path.join(path, "etcd", "ca.crt")
    ca_key_fn = os.path.join(path, "etcd", "ca.key")
    ca, ca_key = cert.generate_etcd_ca()

    cert.dump_to_file(ca_fn, "FILETYPE_PEM", ca, "certificate")
    cert.dump_to_file(ca_key_fn, "FILETYPE_PEM", ca_key, "privatekey")

    for index, filename in enumerate(filenames.split()):
        cert_fn = os.path.join(path, "etcd", "%s.crt" % filename)
        cert_key_fn = os.path.join(path, "etcd", "%s.key" % filename)
        ip = ips.split()[index]

        crt, key = cert.generate_etcd_cert(ca, ca_key, ip=ip)

        cert.dump_to_file(cert_fn, "FILETYPE_PEM", crt, "certificate")
        cert.dump_to_file(cert_key_fn, "FILETYPE_PEM", key, "privatekey")
