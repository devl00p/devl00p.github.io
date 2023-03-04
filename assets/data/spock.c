/*---------------------------------------------+
 |      Spock v0.1 - devloop - 27 oct 2004     |
 +---------------------------------------------+
 |      Just launch the executable as root     +
 +---------------------------------------------*/
#include <stdio.h>
#include <netinet/in.h>
#include <netdb.h>
#include <errno.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <time.h>

#define MAXBUFLEN 100

char interfaces[5][10];
long ips[5];

void banner()
{
  printf("\t>>>>> SPOCK V0.1 <<<<<\n\n");
}

int load_interfaces()
{
  FILE *proc_net_dev;
  char buffer[256];
  char *name;
  char *sep;
  int i;
  struct ifreq ifr;
  int sock;
  struct sockaddr_in s_in;
  
  for(i=0;i<5;i++)
  {
    *interfaces[i]=0;
    ips[i]=0;
  }
  
  printf("[*] Loading interfaces...\n");
  proc_net_dev=fopen("/proc/net/dev","r");
  if(proc_net_dev==NULL)
  {
    perror("fopen");
    exit(1);
  }
  fgets(buffer,256,proc_net_dev);
  fgets(buffer,256,proc_net_dev);
  i=0;
  while(!feof(proc_net_dev))
  {
    name=buffer;
    if(fgets(buffer,256,proc_net_dev)==NULL)
      break;
    sep=strrchr(buffer,':');
    if(sep)
      *sep=0;
    while(*name==' ')name++;
    sock=socket(AF_INET,SOCK_DGRAM,0);
    strcpy(ifr.ifr_name,name);
    if(ioctl(sock,SIOCGIFADDR,&ifr)<0)
      continue;
    else
    {
      strcpy(interfaces[i],name);
      memcpy(&s_in,&(ifr.ifr_addr),sizeof(struct sockaddr));
      ips[i]=s_in.sin_addr.s_addr;
      printf("Found address   %-15s on interface %s\n",inet_ntoa(ips[i]),interfaces[i]);
      i++;
    }
    close(sock);
  }
  printf("\n");
  return i;
}

void print_time()
{
  time_t t;
  struct tm *tme;

  t=time(NULL);
  tme=localtime(&t);
  printf("\n%02u:%02u:%02u ",tme->tm_hour,tme->tm_min,tme->tm_sec);
}

int isopen(int port)
{
  char buffer[200];
  FILE *proc_net_tcp;
  int i=0;
  int local_port;
  int ok=0;

  proc_net_tcp=fopen("/proc/net/tcp","r");
  if(proc_net_tcp==NULL)
  {
    perror("fopen");
    exit(1);
  }
  do
  {
    fgets(buffer,sizeof(buffer),proc_net_tcp);
    if(i)
    {
      if(strlen(buffer)>25)
      {
	strtok(buffer," :");
	strtok(NULL," :");
	sscanf((char *)strtok(NULL," :"),"%X",&local_port);
	if(port==local_port)
	{
	  ok=1;
	  break;
	}
      }
    }
    i++;
  } while (!feof(proc_net_tcp));
  fclose(proc_net_tcp);
  return ok;
}

int filter_ip(long dst)
{
  int i=0;
  while(ips[i]!=0)
  {
    if(ips[i++]==dst)return 0;
  }
  return 1;
}

void process_ip(struct iphdr *ip)
{
  print_time();
  printf("Malformed TCP paquet ");
  printf("ttl=%d",ip->ttl);
}

int process_tcp(struct iphdr *ip,struct tcphdr *tcp)
{
  int virgule=0;
  if(!isopen(ntohs(tcp->dest)) && !(tcp->ack))
  {
    print_time();
    printf("Knock port %5d [",ntohs(tcp->dest));
    if(tcp->syn)
    {
      printf("S");
      virgule++;
    }
    if(tcp->ack)
    {
      if(virgule)printf(",");
      printf("A");
      virgule++;
    }
    if(tcp->rst)
    {
      if(virgule)printf(",");
      printf("R");
      virgule++;
    }
    if(tcp->urg)
    {
      if(virgule)printf(",");
      printf("U");
      virgule++;
    }
    if(tcp->fin)
    {
      if(virgule)printf(",");
      printf("F");
    }
    printf("] from %s:%d",inet_ntoa(ip->saddr),ntohs(tcp->source));
    return 1;
  }
  return 0;
}

void printable(char *data,int i,int j)
{
  for(;j<i;j++)
  {
    if(isprint(data[j]))
      printf("%c",data[j]);
    else
      printf(".");
  }
}

void print_data(char *data,int length)
{
  int i,j;
  for(i=0,j=0;i<length;i++)
  {
    if((i % 20)==0)
    {
      if(i!=0)
      {
	printf(" | ");
	printable(data,i,j);
	j+=i-j;
      }
      printf("\n ");
    }
    if((i % 4)==0)
      printf(" ");
    printf("%02X",(unsigned char)data[i]);
  }
  printf(" | ");
  printable(data,i,j);
  printf("\n");
}

int main(int argc,char *argv[])
{
  int sock;
  char buffer[MAXBUFLEN];
  struct iphdr *ip;
  struct tcphdr *tcp;
  char *data;
  int n,i;

  banner();

  n=load_interfaces();

  if(geteuid())
  {
    printf("L'utilisation de ce programme nécessite les droits root\n");
    exit(1);
  }

  if((sock=socket(PF_INET,SOCK_RAW,IPPROTO_TCP))==-1)
  {
    perror("socket");
    exit(1);
  }

  ip=(struct iphdr*)buffer;
  tcp=(struct tcphdr*)(buffer+sizeof(struct iphdr));
  data=buffer+sizeof(struct iphdr)+sizeof(struct tcphdr);
  
  printf("\n[*] Listening anormal traffic...");

  while(n=read(sock,buffer,sizeof(buffer)))
  {
    // la ligne suivante est commente en attente d'une prochaine evolution
    // (detection du mode promiscuous et utilisation en parallele a un sniffer)
    //if(filter_ip(ip->daddr))continue;
    if((n<(sizeof(struct iphdr)+sizeof(struct tcphdr))) && (n>=sizeof(struct iphdr)))
    {
      // Paquet TCP malforme. Peut etre un protoscan.
      process_ip(ip);
    }
    else if(n>=(sizeof(struct iphdr)+sizeof(struct tcphdr)))
    {
      //if n=40 -> probablement un port scan furtif (avec nmap ou autre)
      //if n>40 -> probablement un port scan 'connect'
      if(process_tcp(ip,tcp))
	if(n>40)print_data(data,n-40);
      
    }
  }
  close(sock);
  return 0;
}
