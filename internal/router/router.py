"""
@Time   : 2024/12/1 05:30
@Author : Leslie
@File   : router.py
"""

from dataclasses import dataclass
from flask import Flask, Blueprint
from injector import inject

from internal.handler import (
    AppHandler,
    BuiltinToolHandler,
    ApiToolHandler,
    UploadFileHandler,
    DatasetHandler,
    DocumentHandler,
    SegmentHandler,
    OAuthHandler,
    AccountHandler,
    AuthHandler,
    AIHandler,
    ApiKeyHandler,
    OpenapiHandler,
    BuiltinAppHandler,
)


@inject
@dataclass
class Router:
    """路由"""

    app_handler: AppHandler
    builtin_tool_handler: BuiltinToolHandler
    api_tool_handler: ApiToolHandler
    upload_file_handler: UploadFileHandler
    dataset_handler: DatasetHandler
    document_handler: DocumentHandler
    segment_handler: SegmentHandler
    oauth_handler: OAuthHandler
    account_handler: AccountHandler
    auth_handler: AuthHandler
    ai_handler: AIHandler
    api_key_handler: ApiKeyHandler
    openapi_handler: OpenapiHandler
    builtin_app_handler: BuiltinAppHandler

    def register_router(self, app: Flask):
        """注册路由"""
        bp = Blueprint("llmops", __name__, url_prefix="")
        openapi_bp = Blueprint("openapi", __name__, url_prefix="")

        bp.add_url_rule("/ping", view_func=self.app_handler.ping)
        bp.add_url_rule(
            "/apps/<uuid:app_id>/conversations",
            methods=["POST"],
            view_func=self.app_handler.debug_chat,
        )

        bp.add_url_rule(
            "/apps", methods=["POST"], view_func=self.app_handler.create_app
        )
        bp.add_url_rule("/apps/<uuid:app_id>", view_func=self.app_handler.get_app)
        bp.add_url_rule(
            "/apps/<uuid:app_id>/draft-app-config",
            view_func=self.app_handler.get_draft_app_config,
        )
        bp.add_url_rule(
            "/apps/<uuid:app_id>/draft-app-config",
            methods=["PUT"],
            view_func=self.app_handler.update_draft_app_config,
        )
        bp.add_url_rule(
            "/apps/<uuid:app_id>/publish",
            methods=["POST"],
            view_func=self.app_handler.publish_app_config,
        )
        bp.add_url_rule(
            "/apps/<uuid:app_id>/publish-histories",
            view_func=self.app_handler.get_publish_histories,
        )
        bp.add_url_rule(
            "/apps/<uuid:app_id>/cancel-publish",
            methods=["POST"],
            view_func=self.app_handler.cancel_publish,
        )
        bp.add_url_rule(
            "/apps/<uuid:app_id>/fallback-history",
            methods=["POST"],
            view_func=self.app_handler.fallback_history,
        )
        bp.add_url_rule(
            "/apps/<uuid:app_id>/summary",
            view_func=self.app_handler.get_app_debug_summary,
        )
        bp.add_url_rule(
            "/apps/<uuid:app_id>/summary",
            methods=["PUT"],
            view_func=self.app_handler.update_app_debug_summary,
        )
        bp.add_url_rule(
            "/apps/<uuid:app_id>/conversations/debug",
            methods=["DELETE"],
            view_func=self.app_handler.delete_app_debug_conversations,
        )
        bp.add_url_rule(
            "/apps/<uuid:app_id>/conversations/tasks/<uuid:task_id>/stop",
            methods=["POST"],
            view_func=self.app_handler.stop_debug_task,
        )
        bp.add_url_rule(
            "/apps/<uuid:app_id>/conversations/messages",
            view_func=self.app_handler.get_conversation_messages_with_page,
        )
        bp.add_url_rule(
            "/apps/<uuid:app_id>",
            methods=["PUT"],
            view_func=self.app_handler.update_app,
        )
        bp.add_url_rule(
            "/apps/<uuid:app_id>",
            methods=["DELETE"],
            view_func=self.app_handler.delete_app,
        )
        bp.add_url_rule("/apps", view_func=self.app_handler.get_apps_pagination)
        bp.add_url_rule(
            "/apps/<uuid:app_id>/copy",
            methods=["POST"],
            view_func=self.app_handler.copy_app,
        )

        # built-in tools
        bp.add_url_rule(
            "/builtin-tools/categories",
            view_func=self.builtin_tool_handler.get_builtin_tools_categories,
        )
        bp.add_url_rule(
            "/builtin-tools", view_func=self.builtin_tool_handler.get_builtin_tools
        )
        bp.add_url_rule(
            "/builtin-tools/<string:provider_name>/tools/<string:tool_name>",
            view_func=self.builtin_tool_handler.get_provider_tool,
        )
        bp.add_url_rule(
            "/builtin-tools/<string:provider_name>/icon",
            view_func=self.builtin_tool_handler.get_provider_icon,
        )

        # api tools
        bp.add_url_rule(
            "/api-tools/validate-openapi-schema",
            methods=["POST"],
            view_func=self.api_tool_handler.validate_openapi_schema,
        )
        bp.add_url_rule(
            "/api-tools",
            methods=["POST"],
            view_func=self.api_tool_handler.create_api_tools,
        )
        bp.add_url_rule(
            "/api-tools/<uuid:provider_id>",
            view_func=self.api_tool_handler.get_api_tools_provider,
        )
        bp.add_url_rule(
            "/api-tools/<uuid:provider_id>/tools/<string:tool_name>",
            view_func=self.api_tool_handler.get_api_tool,
        )
        bp.add_url_rule(
            "/api-tools/<uuid:provider_id>",
            methods=["DELETE"],
            view_func=self.api_tool_handler.delete_api_tool_provider,
        )
        bp.add_url_rule(
            "/api-tools",
            view_func=self.api_tool_handler.get_api_tools_pagination,
        )
        bp.add_url_rule(
            "/api-tools/<uuid:provider_id>",
            methods=["PUT"],
            view_func=self.api_tool_handler.update_api_tools_provider,
        )

        # Upload file
        bp.add_url_rule(
            "/upload-files/file",
            methods=["POST"],
            view_func=self.upload_file_handler.upload_file,
        )
        bp.add_url_rule(
            "/upload-files/image",
            methods=["POST"],
            view_func=self.upload_file_handler.upload_image,
        )

        # Dataset
        bp.add_url_rule(
            "/datasets",
            methods=["POST"],
            view_func=self.dataset_handler.create_dataset,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>",
            methods=["PUT"],
            view_func=self.dataset_handler.update_dataset,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>",
            view_func=self.dataset_handler.get_dataset,
        )
        bp.add_url_rule(
            "/datasets",
            view_func=self.dataset_handler.get_datasets_pagination,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/hit",
            methods=["POST"],
            view_func=self.dataset_handler.hit_dataset,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/queries",
            view_func=self.dataset_handler.get_dataset_queries,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>",
            methods=["DELETE"],
            view_func=self.dataset_handler.delete_dataset,
        )

        # Document
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents",
            methods=["POST"],
            view_func=self.document_handler.create_documents,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/batch/<string:batch_id>",
            view_func=self.document_handler.get_documents_batch,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>",
            view_func=self.document_handler.get_document,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/name",
            methods=["PUT"],
            view_func=self.document_handler.update_document_name,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents",
            view_func=self.document_handler.get_documents_pagination,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/enabled",
            methods=["PUT"],
            view_func=self.document_handler.update_document_enabled,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>",
            methods=["DELETE"],
            view_func=self.document_handler.delete_document,
        )

        # Segment
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments",
            view_func=self.segment_handler.get_segments_pagination,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments/<uuid:segment_id>",
            view_func=self.segment_handler.get_segment,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments/<uuid:segment_id>/enabled",
            methods=["PUT"],
            view_func=self.segment_handler.update_segment_enabled,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments",
            methods=["POST"],
            view_func=self.segment_handler.create_segment,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments/<uuid:segment_id>",
            methods=["PUT"],
            view_func=self.segment_handler.update_segment,
        )
        bp.add_url_rule(
            "/datasets/<uuid:dataset_id>/documents/<uuid:document_id>/segments/<uuid:segment_id>",
            methods=["DELETE"],
            view_func=self.segment_handler.delete_segment,
        )

        # Authorization
        bp.add_url_rule(
            "/oauth/<string:provider_name>",
            view_func=self.oauth_handler.get_redirect_url,
        )
        bp.add_url_rule(
            "/oauth/authorize/<string:provider_name>",
            methods=["POST"],
            view_func=self.oauth_handler.authorize,
        )
        bp.add_url_rule(
            "/auth/password-login",
            methods=["POST"],
            view_func=self.auth_handler.login,
        )
        bp.add_url_rule(
            "/auth/logout", methods=["POST"], view_func=self.auth_handler.logout
        )

        # Account
        bp.add_url_rule("/account", view_func=self.account_handler.get_account)
        bp.add_url_rule(
            "/account/password",
            methods=["PUT"],
            view_func=self.account_handler.update_password,
        )
        bp.add_url_rule(
            "/account/name",
            methods=["PUT"],
            view_func=self.account_handler.update_name,
        )
        bp.add_url_rule(
            "/account/avatar",
            methods=["PUT"],
            view_func=self.account_handler.update_avatar,
        )

        # AI
        bp.add_url_rule(
            "/ai/optimize-prompt",
            methods=["POST"],
            view_func=self.ai_handler.optimize_prompt,
        )
        bp.add_url_rule(
            "/ai/suggested-questions",
            methods=["POST"],
            view_func=self.ai_handler.suggested_questions,
        )

        # OpenAPI
        bp.add_url_rule(
            "/openapi/api-keys",
            methods=["POST"],
            view_func=self.api_key_handler.create_api_key,
        )
        bp.add_url_rule(
            "/openapi/api-keys/<uuid:api_key_id>",
            methods=["DELETE"],
            view_func=self.api_key_handler.delete_api_key,
        )
        bp.add_url_rule(
            "/openapi/api-keys/<uuid:api_key_id>",
            methods=["PUT"],
            view_func=self.api_key_handler.update_api_key,
        )
        bp.add_url_rule(
            "/openapi/api-keys/<uuid:api_key_id>/is-active",
            methods=["PUT"],
            view_func=self.api_key_handler.update_api_key_active,
        )
        bp.add_url_rule(
            "/openapi/api-keys",
            view_func=self.api_key_handler.get_api_keys_pagination,
        )
        openapi_bp.add_url_rule(
            "/openapi/chat",
            methods=["POST"],
            view_func=self.openapi_handler.chat,
        )

        # Builtin App
        bp.add_url_rule(
            "/builtin-apps/app-categories",
            view_func=self.builtin_app_handler.get_builtin_app_categories,
        )
        bp.add_url_rule(
            "/builtin-apps",
            view_func=self.builtin_app_handler.get_builtin_apps,
        )
        bp.add_url_rule(
            "/builtin-apps/add-builtin-app-to-space",
            methods=["POST"],
            view_func=self.builtin_app_handler.add_builtin_app_to_space,
        )

        app.register_blueprint(bp)
        app.register_blueprint(openapi_bp)
