// Fanotify example security program. Used for performance testing.
// This program is a modified version of the example located at https://man7.org/linux/man-pages/man7/fanotify.7.html
#include <cstring>
#include <iostream>
#include <string>

#include <errno.h>
#include <fcntl.h>
#include <limits.h>
#include <poll.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/fanotify.h>
#include <sys/wait.h>
#include <unistd.h>

static void handle_events(int fd)
{
   const struct fanotify_event_metadata *metadata;
   struct fanotify_event_metadata buf[200];
   ssize_t len;
   struct fanotify_response response;


   for (;;) {


       len = read(fd, buf, sizeof(buf));
       if (len == -1 && errno != EAGAIN) {
           perror("read");
           exit(EXIT_FAILURE);
       }


       if (len <= 0)
           break;


       metadata = buf;


       while (FAN_EVENT_OK(metadata, len)) {


           if (metadata->vers != FANOTIFY_METADATA_VERSION) {
               fprintf(stderr,
                       "Mismatch of fanotify metadata version.\n");
               exit(EXIT_FAILURE);
           }


           if (metadata->fd >= 0) {


               if (metadata->mask & FAN_OPEN_PERM) {
                   // printf("FAN_OPEN_PERM: ");


                   response.fd = metadata->fd;
                   response.response = FAN_ALLOW;
                   int result = write(fd, &response, sizeof(response));
                   if (result == -1) {
                        std::cout << "WRITE ERROR " << std::string(strerror(result)) << std::endl;
                   }
               }



               close(metadata->fd);
           }


           metadata = FAN_EVENT_NEXT(metadata, len);
       }
   }
}

int main()
{
   int fanotify_fd, poll_num;
   struct pollfd poll_fd;
   fanotify_fd = fanotify_init(FAN_CLOEXEC | FAN_CLASS_CONTENT | FAN_NONBLOCK,
                      O_RDONLY | O_LARGEFILE);


   if (fanotify_mark(fanotify_fd, FAN_MARK_ADD | FAN_MARK_MOUNT,
                     FAN_OPEN_PERM | FAN_CLOSE_WRITE, AT_FDCWD,
                     "/") == -1) {
       perror("fanotify_mark");
       exit(EXIT_FAILURE);
   }

   poll_fd.fd = fanotify_fd;
   poll_fd.events = POLLIN;

   while (1) {
       poll_num = poll(&poll_fd, 1, -1);
       if (poll_num == -1) {
           if (errno == EINTR)
               continue;

           perror("poll");
           exit(EXIT_FAILURE);
       }

       if (poll_num > 0) {
           if (poll_fd.revents & POLLIN) {
               handle_events(fanotify_fd);
           }
       }
   }

   printf("Listening for events stopped.\n");
   exit(EXIT_SUCCESS);
}
