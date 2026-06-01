const WS = "ws://127.0.0.1:8000";

// const WS = "wss://claim-backend-4xum.onrender.com";

export function connectInterview(interviewId) {
  return new WebSocket(`${WS}/ws/interview/${interviewId}`);
}