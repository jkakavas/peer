# Copyright 2011 Terena. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.

#    2. Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#        and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY TERENA ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL TERENA OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of Terena.

from django.conf import settings

NAMESPACES = {
    'xml': 'http://www.w3.org/XML/1998/namespace',
    'xs': 'xs="http://www.w3.org/2001/XMLSchema',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'md': 'urn:oasis:names:tc:SAML:2.0:metadata',
    'mdui': 'urn:oasis:names:tc:SAML:metadata:ui',
    'ds': 'http://www.w3.org/2000/09/xmldsig#',
    'saml': 'urn:oasis:names:tc:SAML:2.0:assertion',
    'samlp': 'urn:oasis:names:tc:SAML:2.0:protocol',
    }

SAML_METADATA_NAMESPACE = NAMESPACES['md']


def addns(node_name, namespace=SAML_METADATA_NAMESPACE):
    '''Return a node name qualified with the XML namespace'''
    return '{' + namespace + '}' + node_name


def delns(node, namespace=SAML_METADATA_NAMESPACE):
    return node.replace('{' + namespace + '}', '')


def add_previous_revisions(revisions):
    prev, revs = '', []
    for rev in revisions[::-1]:
        if prev:
            rev['previous'] = prev
        prev = rev['versionid']
        revs.append(rev)
    return reversed(revs)


def expand_settings_permissions(include_xpath=True):
    permissions = []

    if hasattr(settings, 'METADATA_PERMISSIONS'):
        perm_setts = settings.METADATA_PERMISSIONS
        for prefix in ('add', 'delete', 'modify'):
            for xpath, name, desc in perm_setts:
                perm_class = '_'.join((prefix, name))
                perm_desc = ' '.join(('Can', prefix.capitalize(), desc))
                exp_perms = [perm_class, perm_desc]
                if include_xpath:
                    exp_perms.insert(0, xpath)
                permissions.append(tuple(exp_perms))

    return tuple(permissions)


def parse_entity_group_query(query):
    """ Query must look like the query string of a feed.
        Query can be a a key-value tuple or a basestring.

        TODO: Document 'specification' for query.
    """
    if isinstance(query, basestring):
        try:
            query = (tuple(y.split('='))
                      for y in (x for x in query.split('&'))
                      )
        except ValueError:
            return None
        else:
            # TODO: there should be a way to avoid this fix
            # string partition? list zipping?
            query = tuple((x[0], None) for x in query if len(x) < 2)

    tags = list()
    tags_w_values = list()
    tags_w_attrs = list()
    try:
        for k, v in query:
            if '$' in k:
                tag, attr = k.split('$')
                tags_w_attrs.append((tag, attr, v))
            elif v:
                tags_w_values.append((k, v))
            else:
                tags.append(k)
        return dict(tags=tuple(tags),
                    tags_w_values=tuple(tags_w_values),
                    tags_w_attrs=tuple(tags_w_attrs))

    except ValueError:
        return None
