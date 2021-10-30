import os
from typing import Optional
from flask.helpers import url_for
from flask_login.utils import (
    login_user,
    login_required,
    logout_user,
)
import requests
from flask import Flask, redirect, request
from oauthlib.oauth2 import WebApplicationClient
import requests
from enum import Enum, auto, unique
from http import HTTPStatus
import json

from localhigh.gateways.user import User


@unique
class Provider(Enum):
    GOOGLE = auto()
    GITHUB = auto()


_GOOGLE_CLIENT_ID = os.environ.get("LOCALHIGH_GOOGLE_CLIENT_ID", None)
_GOOGLE_CLIENT_SECRET = os.environ.get("LOCALHIGH_GOOGLE_CLIENT_SECRET", None)
_GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


def _get_google_client() -> WebApplicationClient:
    if 'google_auth' not in g:
        g.google_auth_client = WebApplicationClient(_GOOGLE_CLIENT_ID)
    return g.google_auth_client


def _get_google_provider_cfg() -> dict:
    resp = requests.get(_GOOGLE_DISCOVERY_URL)
    if resp.ok:
        return resp.json()
    return {}


def _authorize_google(uri) -> Optional[str]:
    client = _get_google_client()
    authorization_endpoint = _get_google_provider_cfg().get(
        "authorization_endpoint",
    )
    if authorization_endpoint:
        return client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=uri + "/google",
            scope=["openid", "email"],
        )
    return None


def _authenticate_google_token(client: WebApplicationClient):
    code = request.args('code')
    token_endpoint = _get_google_provider_cfg().get(
        'token_endpoint',
    )
    if token_endpoint is None:
        raise ValueError() 
    token_url, headers, body = client.prepare_token_request(
       token_endpoint,
       authorization_response=request.url,
       redirect_url=request.base_url,
       code=code
    )
    token_response = requests.post(
       token_url,
       headers=headers,
       data=body,
       auth=(_GOOGLE_CLIENT_ID, _GOOGLE_CLIENT_SECRET),
    )
    if token_response.ok:
        client.parse_request_body_response(json.dumps(token_response.json()))
    else:
        raise ValueError()


def _authenticate_google_user_info(
    client: WebApplicationClient,
) -> tuple[str, str, str]:
    userinfo_endpoint = _get_google_provider_cfg().get(
        'userinfo_endpoint',
    )
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)    
    if userinfo_response.ok:
        userinfo: dict[str, str] = userinfo_response.json()
        if userinfo.get("email_verified"):
            unique_id = userinfo["sub"]
            user_email = userinfo["email"]
            user_name = userinfo["given_name"]
            return (unique_id, user_name, user_email)
        else:
            raise ValueError("User email not available or not verified by Google.")
    else:
        raise ValueError()


def _authenticate_google() -> bool:
    client = _get_google_client()
    try:
        _authenticate_google_token(client)
        id, name, email = _authenticate_google_user_info(client)
        if (user := User.get(id)) is None:
            user = User.create(id, name, email)
        login_user(user)        
    except ValueError:
        return False
    return True


def register_routes(app: Flask):
    @app.get('/api/login')
    def login():
        provider: str = request.args.get('provider', 'google')
        try:
            provider = Provider[provider]
        except KeyError:
            pass

        match provider:
            case Provider.GOOGLE:
                if (uri := _authorize_google(request.base_url)) is None:
                    return (
                        {'error': 'Service incorrectly configured'},
                        HTTPStatus.INTERNAL_SERVER_ERROR,
                    )
                redirect(uri)
            case Provider.GITHUB:
                return (
                    {'error': f'{provider.name} not yet supported'},
                    HTTPStatus.NOT_IMPLEMENTED,
                )
            case _:
                return (
                    {'error': f'{provider} not supported'},
                    HTTPStatus.BAD_REQUEST,
                )
    
    @app.get('/api/login/<provider>')
    def login_callback(provider: str):
        try:
            provider = Provider[provider]
        except KeyError:
            pass
        match provider:
            case Provider.GOOGLE:
                if _authenticate_google():
                    redirect(url_for('index'))
                return (
                    {'error': f'Failed to authenticate with Google'},
                    HTTPStatus.UNAUTHORIZED,
                )
            case Provider.GITHUB:
                return (
                    {'error': f'{provider.name} not yet supported'},
                    HTTPStatus.NOT_IMPLEMENTED,
                )
            case _:
                return (
                    {'error': f'{provider} not supported'},
                    HTTPStatus.BAD_REQUEST,
                )

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("index"))
