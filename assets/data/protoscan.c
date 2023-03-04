/*
 * Protoscan.c
 * devloop - 13/09/2004
 */
#include <stdio.h> // I/O standarts
#include <sys/types.h> // certains type comme u_int8_t
#include <sys/socket.h> // sockets
#include <netinet/ip.h> // structure de l'entete IP
#include <netinet/ip_icmp.h> // structure de l'entete ICMP
#include <netdb.h> // pour les get***by***()
#include <unistd.h> // pour usleep

/* Les resultats seront stockes dans ce tableau global */
int results[140];

void usage(char *prog)
{
    printf("Usage: %s <host>\n",prog);
    printf("\t-- devloop 2004 --\n\n");
    exit(1);
}

/* Conversion nom d'hote -> unsigned long */
u_long resolve (char *host) 
{
    struct in_addr in; 
    struct hostent *he; 
    
    if((in.s_addr=inet_addr(host))==-1) 
    { 
	if((he=(struct hostent*)gethostbyname(host))==NULL) 
	{ 
            herror("Resolving victim host"); 
	    exit(1); 
	} 
	memcpy((caddr_t)&in, he->h_addr, he->h_length); 
    }
    return(in.s_addr); 
}

/* Calculer le checksum d'un entete IP */
/* Fonction trouve sur le web */
u_short in_cksum(u_short *addr, int len)
{
        u_short i = 0, *word = addr;
        u_long acc = 0;

        while(i++ < len / 2)
                acc += *(word++);

        return ~(*(u_short*)&acc + *((u_short*)&acc + 1));
}

/* Envoyer les paquets generes par nos soins */
void launch_scan(int fd, unsigned long dst)
{
    struct iphdr *ip_header;
    char data[sizeof(*ip_header)];
    struct sockaddr_in to;
    u_int8_t proto;

    ip_header=(struct iphdr*)data;
    memset(data,0,sizeof(data));
    ip_header->ihl=5; // l'en-tete a une taille de 5 mots de 32 bits
    ip_header->version=4; // IPv4
    ip_header->tot_len=htons(sizeof(data));
    ip_header->ttl=64;
    ip_header->daddr=dst;
    /* Les autres parametres sont remplis automatiquement par le kernel */
    to.sin_addr.s_addr=dst;
    to.sin_family=AF_INET;
    to.sin_port=0;

    for(proto=0;proto<140;proto++)
    {
        /* laisser un peu de temps à la victime de respirer
           en plus cela augmente l'efficacite de la partie "serveur" */
	usleep(5);
        /* A chaque boucle on incremente le champ protocol */
	ip_header->protocol=proto;
	ip_header->check=in_cksum((unsigned short*)ip_header,sizeof(*ip_header));
	if(sendto(fd,data,sizeof(data),0,(struct sockaddr*)&to,sizeof(to))==-1)
	{
	    perror("echec sendto()");
	    exit(1);
	}

    }
}

/* Traiter les paquets ICMP qui nous parviennent */
int listen_scan(int fd,unsigned long dst)
{
    int n;
    int i;
    char buffer[128];
    struct iphdr *ip_header;
    struct icmphdr *icmp_header;
    struct iphdr *icmp_msg;
    i=0;
    /* Les paquets ICMP nous concernant seront constitues :
     * - d'un entete IP
     * - d'un entete ICMP
     * - d'un second entete IP qui correspond en fait aux donnes ICMP
     * Taille d'un entete IP : 20 octets
     */
    while((n=read(fd,buffer,sizeof(struct iphdr)+sizeof(struct icmphdr)+20)>0))
    {
        /* On ne regarde que les paquets ICMP en provenance de la victime
	 * et qui sont du type Destination/Protocol Unreachable
	 */
	ip_header=(struct iphdr*)buffer;
	icmp_header=(struct icmphdr*)(buffer+sizeof(*ip_header));
	icmp_msg=(struct iphdr*)(buffer+sizeof(*ip_header)+sizeof(*icmp_header));
	if(ip_header->saddr!=dst)continue;
	if(icmp_header->type!=3 || icmp_header->code!=2)continue;
	results[icmp_msg->protocol]=0;
	if(icmp_msg->protocol>130)break;
    }
    return 0;
}

/* Formater les resultats sous une forme "user-friendly" */
void show_results()
{
    int i;
    struct protoent *proto;
    for(i=0;i<130;i++)
    {
	if(results[i]==1)
	{
            /* La fonction getprotobynumber() ne fait que lire
	     * le fichier /etc/protocols. Il est donc necessaire
	     * qu'il soit present sur le système
             */
	    if((proto=(struct protoent*)getprotobynumber(i))!=NULL)
		printf("Protocol %s [%i] supporte\n",proto->p_name,i);
	    else
	    {
                /* Le protocole IP est numerote (4)...
		 * mais l'utilite de le numeroter m'echappe :S
		 */
		if(i!=4) printf("Protocol Unknown [%i] supporte\n",i);
		else printf("Protocol ipv4 [4] supporte\n");
	    }
	}
    }
}

int main(int argc,char *argv[])
{
    int s;
    int s2;
    int pid;
    struct hostent *host;
    unsigned long int target;

    if(argc!=2)usage(argv[0]);
    if(geteuid()!=0)
    {
        /* Les raw-sockets necessitent les droits root */
	printf("You need to be root to launch this proggie\n");
	return 1;
    }
    for(s=0;s<140;s++)results[s]=1;
    if((s=socket(PF_INET,SOCK_RAW,IPPROTO_RAW))==-1)
    {
	perror("echec socket()");
	return 1;
    }
    if((s2=socket(PF_INET,SOCK_RAW,IPPROTO_ICMP))==-1)
    {
	perror("echo socket()");
	return 1;
    }
    target=resolve(argv[1]);

    /* Un processus scanne, l'autre traite les reponses */
    if((pid=fork())==-1)
    {
	perror("echec fork()");
	return 1;
    }
    if(pid==0)
    {
	printf("\tLaunching scan...\n");
	launch_scan(s,target);
    }
    else
    {
	listen_scan(s2,target);
	show_results();
	printf("\tScan done!\n\n");
    }
    close(s);
    /* Le programme renvoie 0 si le scan a fonctionne */
    return 0;
}
