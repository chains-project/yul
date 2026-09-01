#include <glog/logging.h>

int main(int argc, char* argv[]) {
    google::InitGoogleLogging(argv[0]);

    LOG(INFO) << "backend service starting up";
    LOG(WARNING) << "example warning-level log entry";
    VLOG(1) << "example verbose log entry";

    LOG(INFO) << "backend service ready";
    return 0;
}
