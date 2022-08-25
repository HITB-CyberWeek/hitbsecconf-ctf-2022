g++ -static -std=c++2a \
  main.cpp api.cpp fly_redis.cpp router.cpp handlers.cpp validators.cpp session_manager.cpp utils.cpp hasher.cpp \
  -pthread -lpthread -lboost_thread -lboost_system -lboost_timer -lboost_chrono -lrt -lboost_filesystem -lboost_program_options -lboost_regex -lcgicc \
  -fno-stack-protector \
  -o server/app.cgi
