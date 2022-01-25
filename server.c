#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <pthread.h>
#include <sys/types.h>
#include <signal.h>
// COMPILE gcc program.c -lpthread -Wall -o outfile

#define MAX_CLIENTS 100
#define BUFF_SIZE 2048
#define PORT 9090

/* Client structure */
typedef struct{
	struct sockaddr_in address;
	int sockfd;
	int uid;
	char name[32];
} client_t;

client_t *clients[MAX_CLIENTS];
char client_message[BUFF_SIZE];
char buffer[BUFF_SIZE];
pthread_mutex_t clients_mutex = PTHREAD_MUTEX_INITIALIZER;
unsigned int cli_count = 0;
static int uid = 10;

/* Add clients to queue */
void queue_add(client_t *cl){
	pthread_mutex_lock(&clients_mutex);

	for(int i = 0; i < MAX_CLIENTS; i++){
		if(!clients[i]){
			clients[i] = cl;
			break;
		}
	}
	pthread_mutex_unlock(&clients_mutex);
}

/* Remove clients from queue */
void queue_remove(int uid){
	pthread_mutex_lock(&clients_mutex);

	for(int i = 0; i < MAX_CLIENTS; i++){
		if(clients[i]){
			if(clients[i]->uid == uid){
				clients[i] = NULL;
				break;
			}
		}
	}
	pthread_mutex_unlock(&clients_mutex);
}

/* Handle all communication with the client */
void * socketThread(void *arg) {
    cli_count++;
	client_t *cli = (client_t *)arg;
	char name[32];
	int leave_flag = 0;
    int n;

    if(recv(cli->sockfd, name, 32, 0) > 0 && strlen(name) < 32){
        strcpy(cli->name, name);
        printf("New user joined: %s\n", name);
    }
    else {
        printf("ERROR!\n");
        leave_flag = 1;
    }

    while(1) {
        if (leave_flag) break;
        int receiver_start = 0, receiver_end = 0;
        n = recv(cli->sockfd, client_message, BUFF_SIZE, 0);
        if(n < 1) break;
        printf("RECEIVED: %s\n", client_message);

        char *message = malloc(BUFF_SIZE);
        char *receiver = malloc(32*4);
        char *message_out = malloc(BUFF_SIZE);
        strcpy(message, client_message);
        /* Cuts the message to receiver (we need his name) and to clear message */
        for (int i = 0; i < strlen(message)-1; i++){
            if (message[i] == '-' && message[i+1] == '>'){
                receiver_start = i+3;
                i += 2;
            }
            if (message[i] == ':') receiver_end = i-1;
        }
        
        strncpy(receiver, message + receiver_start, receiver_end - receiver_start);
        strncpy(message_out, message + receiver_end + 3, strlen(message) - receiver_end - 3);
        /* Prepares message to send */
        sprintf(message, "%s : %s", name, message_out);
        // printf("SENDING: %s\n", message);
        /* Looking for the receiver and sends to him */
        for (int i = 0; i < cli_count; i++){
            if (!strcmp(clients[i]->name, receiver)) {
                printf("SENDING %s to %s\n", message, clients[i]->name);
                send(clients[i]->sockfd, message, BUFF_SIZE, 0);                
                break;
            }
        }
        /* Sends message back to sender*/
        printf("SENDING %s to %s\n", message, cli->name);
        send(cli->sockfd, message, strlen(message), 0);
        memset(&client_message, 0, BUFF_SIZE);
    }
    printf("Exit socketThread \n");
    close(cli->sockfd);
	queue_remove(cli->uid);
	free(cli);
	cli_count--;

    pthread_exit(NULL);
}

int main(){
    int serverSocket, newSocket;
    struct sockaddr_in serverAddr;
    struct sockaddr_in cli_addr;

    //Create the socket. 
    serverSocket = socket(AF_INET, SOCK_STREAM, 0);

    // Configure settings of the server address struct
    serverAddr.sin_family = AF_INET; 
    serverAddr.sin_port = htons(PORT);
    serverAddr.sin_addr.s_addr = inet_addr("192.168.1.19"); // htonl(INADDR_ANY)

    memset(serverAddr.sin_zero, '\0', sizeof serverAddr.sin_zero);
    bind(serverSocket, (struct sockaddr *) &serverAddr, sizeof(serverAddr));
    
    if(listen(serverSocket, 50) == 0) printf("Listening\n");
    else printf("Error\n");
    pthread_t thread_id;

    while(1) {
        socklen_t clilen = sizeof(cli_addr);
        //Accept call creates a new socket for the incoming connection
        newSocket = accept(serverSocket, (struct sockaddr*)&cli_addr, &clilen);
        // Create client
        client_t *cli = (client_t *)malloc(sizeof(client_t));
		cli->address = cli_addr;
		cli->sockfd = newSocket;
		cli->uid = uid++;
        queue_add(cli);

        if( pthread_create(&thread_id, NULL, &socketThread, (void*)cli) != 0 )
            printf("Failed to create thread\n");

        pthread_detach(thread_id);
        //pthread_join(thread_id,NULL);
    }
    return 0;
}