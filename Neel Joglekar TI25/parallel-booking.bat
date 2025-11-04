@echo off
REM ===== Parallel booking demo for two users =====
REM Replace <api-id> and <region> with your API Gateway HTTP API info

set "URL=https://oxnrouwfta.execute-api.us-east-1.amazonaws.com/book"

REM Open first terminal for User1
start "User1 Booking" cmd /k curl -s -X POST "%URL%" -H "Content-Type: application/json" -d "{\"event_id\":\"e3\",\"name\":\"User1\"}"

REM Open second terminal for User2
start "User2 Booking" cmd /k curl -s -X POST "%URL%" -H "Content-Type: application/json" -d "{\"event_id\":\"e3\",\"name\":\"User2\"}"

REM Exit the batch file
exit























//https://oxnrouwfta.execute-api.us-east-1.amazonaws.com/book