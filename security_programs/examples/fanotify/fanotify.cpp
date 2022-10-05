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
#include <unistd.h>

static void handle_events(int fd)
{
   const struct fanotify_event_metadata *metadata;
   struct fanotify_event_metadata buf[200];
   ssize_t len;
   char path[PATH_MAX];
   ssize_t path_len;
   char procfd_path[PATH_MAX];
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
                   printf("FAN_OPEN_PERM: ");


                   response.fd = metadata->fd;
                   response.response = FAN_ALLOW;
                   int result = write(fd, &response, sizeof(response));
                   if (result == -1) {
                        std::cout << "WRITE ERROR " << std::string(strerror(result)) << std::endl;
                   }
               }


               if (metadata->mask & FAN_CLOSE_WRITE)
                   printf("FAN_CLOSE_WRITE: ");


               snprintf(procfd_path, sizeof(procfd_path),
                        "/proc/self/fd/%d", metadata->fd);
               path_len = readlink(procfd_path, path,
                                   sizeof(path) - 1);
               if (path_len == -1) {
                   perror("readlink");
                   exit(EXIT_FAILURE);
               }

               path[path_len] = '\0';
               printf("File %s\n", path);


               close(metadata->fd);
           }


           metadata = FAN_EVENT_NEXT(metadata, len);
       }
   }
}

int main(int argc, char *argv[])
{
   char buf;
   int fd, poll_num;
   nfds_t nfds;
   struct pollfd fds[2];


   if (argc != 2) {
       fprintf(stderr, "Usage: %s MOUNT\n", argv[0]);
       exit(EXIT_FAILURE);
   }

   printf("Press enter key to terminate.\n");


   fd = fanotify_init(FAN_CLOEXEC | FAN_CLASS_CONTENT | FAN_NONBLOCK,
                      O_RDONLY | O_LARGEFILE);
   if (fd == -1) {
       perror("fanotify_init");
       exit(EXIT_FAILURE);
   }


   if (fanotify_mark(fd, FAN_MARK_ADD | FAN_MARK_MOUNT,
                     FAN_OPEN_PERM | FAN_CLOSE_WRITE, AT_FDCWD,
                     argv[1]) == -1) {
       perror("fanotify_mark");
       exit(EXIT_FAILURE);
   }


   nfds = 2;

   fds[0].fd = STDIN_FILENO;
   fds[0].events = POLLIN;

   fds[1].fd = fd;
   fds[1].events = POLLIN;


   printf("Listening for events.\n");

   while (1) {
       poll_num = poll(fds, nfds, -1);
       if (poll_num == -1) {
           if (errno == EINTR)
               continue;

           perror("poll");
           exit(EXIT_FAILURE);
       }

       if (poll_num > 0) {
           if (fds[0].revents & POLLIN) {


               while (read(STDIN_FILENO, &buf, 1) > 0 && buf != '\n')
                   continue;
               break;
           }

           if (fds[1].revents & POLLIN) {


               handle_events(fd);
           }
       }
   }

   printf("Listening for events stopped.\n");
   exit(EXIT_SUCCESS);
}
