#include <glog/logging.h>

int main(int argc, char* argv[]) {
    google::InitGoogleLogging(argv[0]);

    LOG(INFO) << "backend service starting up";
    LOG(WARNING) << "example warning: cache miss on startup";
    LOG(ERROR) << "example error: could not reach downstream (non-fatal)";

    return 0;
}
