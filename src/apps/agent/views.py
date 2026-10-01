from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .agent import get_agent



from uuid import UUID

class AgentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        message = request.data.get("message")
        thread_id = request.data.get("thread_id")

        if not isinstance(message, str) or not message.strip():
            return Response(
                {"error": "Please provide a valid message"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if thread_id:
            try:
                thread_id = str(UUID(thread_id))
            except (ValueError, TypeError, AttributeError):
                return Response(
                    {"error": "Invalid thread_id"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            from uuid import uuid4
            thread_id = str(uuid4())

        agent = get_agent()

        config = {
            "configurable": {
                "thread_id": f"user_{request.user.id}_{thread_id}"
            }
        }

        
        response = agent.invoke(
                {
                    "question": message.strip(),
                    "user_id": str(request.user.id),
                    "chunks": [],
                    "context": "",
                    "answer": "",
                    "retrieval_good": False,
                    "grounded": False,
                    "retry_count": 0,
                    "relevance_score": 0.0,
                    "relevance_reason": "",
                    "rewritten_question": "",
                },
                config=config,
            )

        return Response({
                "thread_id": thread_id,
                "answer": response.get("answer", ""),
            })

        # except Exception:
        #     return Response(
        #         {"error": "Agent processing failed"},
        #         status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     )
