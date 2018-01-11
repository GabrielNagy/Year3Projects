import ldap
import re
from buildbot import interfaces
from buildbot import util
from twisted.python import log
from zope.interface import implementer


@implementer(interfaces.IEmailLookup)
class IcdCslToEmail(util.ComparableMixin):
    def __init__(self, emailsMap=None):
        self.emailsMap = emailsMap

    def getAddress(self, csl):
        """ It will search first in emailsMap if user is present. If not, it will search against ICD.
        """

        if self.emailsMap and csl in self.emailsMap is not None:
            return self.emailsMap[csl]
        l = ldap.initialize('ldap://ed-p-gl.emea.nsn-net.net')
        binddn = "o=NSN"
        basedn = "o=NSN"

        searchFilter = "uid=" + csl
        searchAttribute = ["mail"]
        searchScope = ldap.SCOPE_SUBTREE
        try:
            l.protocol_version = ldap.VERSION3
            l.simple_bind_s(binddn)
        except ldap.LDAPError as e:
            if type(e.message) == dict and 'desc' in e.message:
                log.msg(e.message['desc'])
            else:
                log.msg(e)
        try:
            ldap_result_id = l.search(basedn, searchScope, searchFilter, searchAttribute)
            result_set = []
            while 1:
                result_type, result_data = l.result(ldap_result_id, 0)
                if (result_data == []):
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:
                        result_set.append(result_data)
            log.msg(result_set)
            match = re.findall(r'[\w\.-]+@[\w\.-]+', str(result_set[0]))
            if match:
                return match[0]

        except ldap.LDAPError as e:
            log.msg(e)
        l.unbind_s()
