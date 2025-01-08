"""
@Time   : 2024/12/1 05:28
@Author : Leslie
@File   : app_handler.py
"""

from flask import request
from flask_login import login_required, current_user
from internal.schema import DebugChatRequestSchema
from internal.schema.app_schema import (
    CreateAppReqSchema,
    FallbackHistoryReqSchema,
    GetAppConfigPublishHistoriesResSchema,
    GetAppResSchema,
    GetConversationMessagesReqSchema,
    UpdateAppDebugSummaryReqSchema,
    UpdateAppReqSchema,
)
from internal.service import (
    AppService,
)
from pkg.response import (
    validate_error_json,
    success_json,
    success_message,
)
from injector import inject
from dataclasses import dataclass
from uuid import UUID
from pkg.pagination import PaginationReq, PageModel
from pkg.response import compact_generate_response


@inject
@dataclass
class AppHandler:
    app_service: AppService

    def ping(self):
        return success_message("pong")

    @login_required
    def debug_chat(self, app_id: UUID):
        req = DebugChatRequestSchema()
        if not req.validate():
            return validate_error_json(req.errors)

        response = self.app_service.debug_chat(app_id, req.query.data, current_user)
        return compact_generate_response(
            response=response,
        )

    @login_required
    def create_app(self):
        req = CreateAppReqSchema()
        if not req.validate():
            return validate_error_json(req.errors)
        app = self.app_service.create_app(req, current_user)
        return success_json({"id": app.id})

    @login_required
    def get_app(self, app_id: UUID):
        result = self.app_service.get_app(app_id, current_user)
        return success_json(GetAppResSchema().dump(result))

    @login_required
    def update_app(self, id: UUID):
        app = self.app_service.update_app(id)
        return success_message(f"更新应用成功, 应用名称: {app.name}")

    @login_required
    def delete_app(self, id: UUID):
        app = self.app_service.delete_app(id)
        return success_message(f"删除应用成功, 应用ID: {app.id}")

    @login_required
    def get_draft_app_config(self, app_id: UUID):
        config = self.app_service.get_draft_app_config(app_id, current_user)
        return success_json(config)

    @login_required
    def update_draft_app_config(self, app_id: UUID):
        draft_app_config = request.get_json(force=True, silent=True) or {}
        self.app_service.update_draft_app_config(app_id, draft_app_config, current_user)
        return success_message("更新草稿配置成功")

    @login_required
    def publish_app_config(self, app_id: UUID):
        self.app_service.publish_app_config(app_id, current_user)
        return success_message("发布/更新应用配置信息成功")

    @login_required
    def get_publish_histories(self, app_id: UUID):
        req = PaginationReq(request.args)
        if not req.validate():
            return validate_error_json(req.errors)
        histories, paginator = self.app_service.get_publish_histories(
            app_id, req, current_user
        )
        schema = GetAppConfigPublishHistoriesResSchema(many=True)
        return success_json(PageModel(schema.dump(histories), paginator))

    @login_required
    def cancel_publish(self, app_id: UUID):
        self.app_service.cancel_publish(app_id, current_user)
        return success_message("取消发布应用配置成功")

    @login_required
    def fallback_history(self, app_id: UUID):
        req = FallbackHistoryReqSchema()
        if not req.validate():
            return validate_error_json(req.errors)
        self.app_service.fallback_history(
            app_id, req.app_config_version_id.data, current_user
        )
        return success_message("回退历史配置至草稿成功")

    @login_required
    def get_app_debug_summary(self, app_id: UUID):
        summary = self.app_service.get_app_debug_summary(app_id, current_user)
        return success_json({"summary": summary})

    @login_required
    def update_app_debug_summary(self, app_id: UUID):
        req = UpdateAppDebugSummaryReqSchema()
        if not req.validate():
            return validate_error_json(req.errors)
        self.app_service.update_app_debug_summary(
            app_id, req.summary.data, current_user
        )
        return success_message("更新应用调试摘要成功")

    @login_required
    def delete_app_debug_conversations(self, app_id: UUID):
        self.app_service.delete_app_debug_conversations(app_id, current_user)
        return success_message("删除应用调试对话成功")

    @login_required
    def stop_debug_task(self, app_id: UUID, task_id: UUID):
        self.app_service.stop_debug_task(app_id, task_id, current_user)
        return success_message("停止调试任务成功")

    @login_required
    def get_conversation_messages_with_page(self, app_id: UUID):
        req = GetConversationMessagesReqSchema(request.args)
        if not req.validate():
            return validate_error_json(req.errors)

        result, paginator = self.app_service.get_conversation_messages_with_page(
            app_id, req, current_user
        )
        return success_json(PageModel(result, paginator))

    @login_required
    def delete_app(self, app_id: UUID):
        self.app_service.delete_app(app_id, current_user)
        return success_message(f"删除应用成功")

    @login_required
    def update_app(self, app_id: UUID):
        req = UpdateAppReqSchema()
        if not req.validate():
            return validate_error_json(req.errors)
        self.app_service.update_app(app_id, current_user, req)
        return success_message(f"更新应用成功")
