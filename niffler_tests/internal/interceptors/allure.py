import grpc
from typing import Callable
from google.protobuf.message import Message
from google.protobuf.json_format import MessageToJson
import allure


class AllureInterceptor(grpc.UnaryUnaryClientInterceptor):
    def intercept_unary_unary(
        self,
        continuation: Callable,
        client_call_details: grpc.ClientCallDetails,
        request: Message,
    ):
        with allure.step(client_call_details.method):
            allure.attach(
                MessageToJson(request),
                name="request",
                attachment_type=allure.attachment_type.JSON,
            )

            future_response = continuation(client_call_details, request)

            response = future_response.result()
            allure.attach(
                MessageToJson(response),
                name="response",
                attachment_type=allure.attachment_type.JSON,
            )

            return future_response
