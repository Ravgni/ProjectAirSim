#ifndef MavLinkCom_HighPriorityThread_hpp
#define MavLinkCom_HighPriorityThread_hpp

#include <string>
#include <thread>

namespace mavlink_utils {

class CurrentThread {
 public:
  // make the current thread run with maximum priority.
  static bool setMaximumPriority();

  // set a nice name on the current thread which aids in debugging.
  static bool setThreadName(const std::string& name);
};

}  // namespace mavlink_utils

#endif