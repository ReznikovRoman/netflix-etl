from rest_framework.authentication import TokenAuthentication as _TokenAuthentication


class TokenAuthentication(_TokenAuthentication):
    keyword = 'Bearer'
