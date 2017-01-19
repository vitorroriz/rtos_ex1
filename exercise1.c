#include <stdio.h>
#include <unistd.h>
#include <pthread.h>

void *increment();
void *decrement();

int shared_resource = 0;


int main()
{
	pthread_t p_th1, p_th2;

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
	shared_resource++;
	usleep(1000);
	//printf("a");
	}

		return NULL;
}



void *decrement()
{
	int i;

	for (i=0; i<100; i++){
	shared_resource--;
	usleep(1000);
	//printf("b");
	}
	return NULL;	
}
