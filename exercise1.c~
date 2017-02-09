#include <stdio.h>
#include <unistd.h>
#include <pthread.h>

void *increment();
void *decrement();

int shared_resource = 0;
pthread_mutex_t resource1;

int main()
{

	pthread_t p_th1, p_th2;

    if (pthread_mutex_init(&resource1, NULL) != 0)
	{
    printf("\n mutex init failed\n");
    return 1;
	}


	pthread_create(&p_th1, NULL, increment, NULL);
	pthread_create(&p_th2, NULL, decrement, NULL);


	pthread_join(p_th1, NULL);
	pthread_join(p_th2, NULL);

	printf("The amount of shared resource after manipulation by threads is: %i\n", shared_resource);



	return 0;

}





void *increment()
{
	int i;

	for (i=0; i<100; i++){
	pthread_mutex_lock(&resource1);
	shared_resource++;
	pthread_mutex_unlock(&resource1);
	usleep(1000);
	//printf("a");
	}

		return NULL;
}



void *decrement()
{
	int i;

	for (i=0; i<99; i++){
	pthread_mutex_lock(&resource1);
	shared_resource--;
	pthread_mutex_unlock(&resource1);
	usleep(1000);
	//printf("b");
	}
	return NULL;	
}
