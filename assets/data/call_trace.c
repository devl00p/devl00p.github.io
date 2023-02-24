#include <sys/ptrace.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>
#include <sys/user.h>
#include <sys/syscall.h>
#include <stdio.h>
#include <stdlib.h>

char *get_syscall_name(long syscall)
{
  switch(syscall) {
    case SYS_restart_syscall:
      return "restart_syscall";
    case SYS_exit:
      return "exit";
    case SYS_fork:
      return "fork";
    case SYS_read:
      return "read";
    case SYS_write:
      return "write";
    case SYS_open:
      return "open";
    case SYS_close:
      return "close";
    case SYS_waitpid:
      return "waitpid";
    case SYS_creat:
      return "creat";
    case SYS_link:
      return "link";
    case SYS_unlink:
      return "unlink";
    case SYS_execve:
      return "execve";
    case SYS_chdir:
      return "chdir";
    case SYS_time:
      return "time";
    case SYS_mknod:
      return "mknod";
    case SYS_chmod:
      return "chmod";
    case SYS_lchown:
      return "lchown";
    case SYS_break:
      return "break";
    case SYS_oldstat:
      return "oldstat";
    case SYS_lseek:
      return "lseek";
    case SYS_getpid:  // 20
      return "getpid";
    case SYS_mount:
      return "mount";
    case SYS_umount:
      return "umount";
    case SYS_setuid:
      return "setuid";
    case SYS_getuid:
      return "getuid";
    case SYS_stime:
      return "stime";
    case SYS_ptrace:
      return "ptrace";
    case SYS_alarm:
      return "alarm";
    case SYS_oldfstat:
      return "oldfstat";
    case SYS_pause:
      return "pause";
    case SYS_utime:
      return "utime";
    case SYS_stty:
      return "stty";
    case SYS_gtty:
      return "gtty";
    case SYS_access:
      return "access";
    case SYS_nice:
      return "nice";
    case SYS_ftime:
      return "ftime";
    case SYS_sync:
      return "sync";
    case SYS_kill:
      return "kill";
    case SYS_rename:
      return "rename";
    case SYS_mkdir:
      return "mkdir";
    case SYS_rmdir:
      return "rmdir";
    case SYS_dup:
      return "dup";
    case SYS_pipe:
      return "pipe";
    case SYS_times:
      return "times";
    case SYS_prof:
      return "prof";
    case SYS_brk:
      return "brk";
    case SYS_setgid:
      return "setgid";
    case SYS_getgid:
      return "getgid";
    case SYS_signal:
      return "signal";
    case SYS_geteuid:
      return "geteuid";
    case SYS_getegid:   // 50
      return "getegid";
    case SYS_umask:     // 60
      return "umask";
    case SYS_dup2:
      return "dup2";
    case SYS_setsid:
      return "setsid";
    case SYS_sigaction:
      return "sigaction";
    case SYS_gettimeofday:
      return "gettimeofday";
    case SYS_select:
      return "select";
    case SYS_symlink:
      return "symlink";
    case SYS_readlink:
      return "readlink";
    case SYS_readdir:
      return "readdir";
    case SYS_mmap:      // 90
      return "mmap";
    case SYS_munmap:
      return "munmap";
    case SYS_truncate:
      return "truncate";
    case SYS_ftruncate:
      return "ftruncate";
    case SYS_setpriority:
      return "setpriority";
    case SYS_socketcall:
      return "socketcall";
    case SYS_stat:
      return "stat";
    case SYS_clone:
      return "clone";
    case SYS_mprotect:
      return "mprotect";


    case SYS_getdents:
      return "getdents";
    case SYS_mremap:
      return "mremap";
    case SYS_poll:
      return "poll";
    case SYS_getcwd:
      return "getcwd";
    case SYS_mmap2:
      return "mmap2";
    case SYS_getuid32:
      return "getuid32";
    case SYS_fstat64:
      return "fstat64";
    case SYS_sched_yield:
      return "sched_yield";
    case SYS_set_thread_area:
      return "set_thread_area";
    case SYS_exit_group:
      return "exit_group";
    case SYS_nanosleep:
      return "nanosleep";
    case SYS_rt_sigaction:
      return "rt_sigaction";
    case SYS_rt_sigprocmask:
      return "rt_sigprocmask";
    case SYS_fgetxattr:
      return "fgetxattr";
    default:
      return "unknown";
  }
}


int main(int argc, char *argv[])
{
  pid_t child;
  const int long_size = sizeof(long);

  if (argc < 2) {
    printf("Usage: %s progname\n", argv[0]);
    return -1;
  }

  child = fork();

  if (!child) {
    // invite le processus parent a tracer
    ptrace(PTRACE_TRACEME, 0, NULL, NULL);
    execl(argv[1], argv[1], NULL);
  } else {
    int status;
    union u {
        long val;
        char chars[long_size];
    }data;
    struct user_regs_struct regs;
    long ins;
    int follow_syscall = 0;

    while (1) {
      // attend que le process fils soit bloque (pret a etre trace)
      wait(&status);

      if (WIFEXITED(status)) {
        // le process est termine, rien ne sert de continuer
        break;
      }

      if (!follow_syscall) {
        // continue l'execution jusqu'au prochain syscall
        ptrace(PTRACE_SYSCALL, child, NULL, NULL);
        follow_syscall = 1;
      } else {
        // on est sur un syscall, lire les registres
        ptrace(PTRACE_GETREGS, child, NULL, &regs);

        printf("[*] %s (%ld)\n", get_syscall_name(regs.orig_eax), regs.orig_eax);
        if (regs.orig_eax == -1) break;

        if (regs.orig_eax == SYS_write) {
          int i = 0;
          int after_ret = 0;

          while (i < 4) {
            ins = ptrace(PTRACE_PEEKTEXT, child, regs.eip, NULL);

            // instruction ret
            if ((ins & 0x000000FF) == 0xc3) {
              after_ret = 1;
              i++;
            }

            // next instruction
            ptrace(PTRACE_SINGLESTEP, child, NULL, NULL);
            wait(&status);
            ptrace(PTRACE_GETREGS, child, NULL, &regs);
            if (after_ret) {
              printf("post-ret [%d] EIP: 0x%08lx\n", i, regs.eip);
              after_ret = 0;
            }
	    if (ins  == 0xffffffff) break;
          }
        }

        ptrace(PTRACE_SINGLESTEP, child, NULL, NULL);
        follow_syscall = 0;
      }
    }
  }
  return 0;
}
