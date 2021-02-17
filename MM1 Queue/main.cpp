/*
 ============================================================================
 Name        : Single_server_queue_simulation.c
 Author      : Khwilo
 Version     :
 Copyright   : Your copyright notice
 Description : Single Server Queue Simulation in C, Ansi-style
 ============================================================================
 */

#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <tuple>
#include <vector>
#include "lcgrand.h" /* Header file for the random-number-generator */
#include "matplotlibcpp.h"

namespace plt = matplotlibcpp;

#define Q_LIMIT 10000 /* Limit on the queue length */
#define BUSY 1 /* Mnemonics for server's being busy */
#define IDLE 0 /* and idle. */

int next_event_type, num_custs_delayed, num_delays_required, num_events, num_in_q, server_status;
float area_num_in_q, area_server_status, mean_interarrival, mean_service, sim_time, time_arrival[Q_LIMIT + 1], time_last_event, time_next_event[3], total_of_delays;
FILE *infile, *outfile;

void initialize(void);
void timing(void);
void arrive(void);
void depart(void);
std::tuple<float, float, float> report(void);
void update_time_avg_stats(void);
float expon(float mean);
void experiment1(void);
void experiment2(void);

int main(void) {
	/* Open input and output files. */
	infile  = fopen("mm1.in", "r");
	outfile = fopen("mm1.out", "w");

	/* Specify the number of events for the timing function */
	num_events = 2;

	/* Read input parameters */
	fscanf(infile, "%f %f %d", &mean_interarrival, &mean_service, &num_delays_required);
	mean_interarrival = mean_interarrival/60;
	mean_service = mean_service/60;

	/* Write report heading and input parameters */
	printf("lambda %11.3f\n\n", mean_interarrival);
	printf("mu %11.3f\n\n", mean_service);
	fprintf(outfile, "Single server queuing system\n\n");
	fprintf(outfile, "Mean interarrival time%11.3f minutes \n\n", mean_interarrival);
	fprintf(outfile, "Mean service time%16.3f minutes\n\n", mean_service);
	fprintf(outfile, "Number of customers%14d\n\n", num_delays_required);

	/*Initialize the simulation */
	initialize();
	experiment1();
	/* Invoke the report generator and end the simulation */
	report();
	experiment2();
	fclose(infile);
	fclose(outfile);

	return 0;
}

void experiment1(void)
{
	/* Run the simulation while more delays are still needed */
	while(num_custs_delayed <  num_delays_required){
		/*Determine the next event */
		timing();

		/* Update time-average statistical accumulators. */
		update_time_avg_stats();

		/* Invoke the appropriate event function */
		switch(next_event_type){
			case 1:
				arrive();
				break;
			case 2:
				depart();
				break;
		}
	}
}

void experiment2(void){

	plt::plot({1,3,2,4});
    plt::show();
	int n = 10;
	// float ratios[10];
	std::vector<float> ratios(n), avglength(n), avgdelay(n), utilization(n);
	for(int i=0,u=1; i<10,u<11; i++,u++)
	{
		ratios.at(i) = (u/10.0);
	}
	for(int i=0;i<10;i++){
		experiment1();
		float len, del, util;
		std::tie(len, del, util) = report();
		avglength.at(i) = len;
		avgdelay.at(i) = del;
		utilization.at(i) = util;
		// printf("%f %f %f", len, del, util);
	}
	plt::figure(1);
	plt::subplot(3,1,1);
	plt::plot(ratios, avglength);
    plt::xlabel("Ratio (ro)");
    plt::ylabel("Avg Q length");

	plt::subplot(3,1,2);
    plt::plot(ratios, avgdelay);
    plt::xlabel("Ratio (ro)");
    plt::ylabel("Avg Q delay (sec)");

    plt::subplot(3,1,3);
    plt::plot(ratios, utilization);
    plt::xlabel("Ratio (ro)");
    plt::ylabel("Util");

	plt::show();
}

void initialize(void){ /* Initialize function. */
	/* Initialize the simulation clock. */
	sim_time = 0;

	/* Initialize the state variables. */
	server_status   = IDLE;
	num_in_q        = 0;
	time_last_event = 0.0;

	/* Initialize the statistical counters. */
	num_custs_delayed  = 0;
	total_of_delays    = 0.0;
	area_num_in_q      = 0.0;
	area_server_status = 0.0;

	/* Initialize the event list. Since no customers are present, the departure (service completion) event is eliminated from consideration. */
	time_next_event[1] = sim_time + expon(mean_interarrival);
	time_next_event[2] = 1.0e+30;
}

void  timing(void){ /* Timing function. */
	int i;
	float min_time_next_event = 1.0e+29;

	next_event_type = 0;
	/* Determine the event type for the next event to occur. */
	for(i = 1; i <= num_events; ++i){
		if(time_next_event[i] < min_time_next_event){
			min_time_next_event = time_next_event[i];
			next_event_type = i;
		}
	}

	/* Check to see whether the event list is empty. */
	if(next_event_type == 0){
		/* The event list is empty, so stop the simulation. */
		fprintf(outfile, "\nEvent list is empty at time %f", sim_time);
		exit(1);
	}

	/* The event list is not empty, so advance the simulation clock. */
	sim_time = min_time_next_event;
}

void arrive(void){ /* Arrival event function. */
	float delay;
	/* Schedule next arrival. */
	time_next_event[1] = sim_time + expon(mean_interarrival);

	/* Check to see whether server is busy. */
	if(server_status == BUSY){
		/* Server is busy so increment the number of customers in the queue. */
		++num_in_q;

		/* Check to see whether an overflow condition exists. */
		if(num_in_q > Q_LIMIT){
			/* The queue has overflowed, so stop the simulation. */
			fprintf(outfile, "\nOverflow of the array time_arrival at");
			fprintf(outfile, " time %f", sim_time);
			exit(2);
		}

		/* There is still room in the queue, so store the time of arrival of the arriving customer at the (new) end of time_arrival. */
		time_arrival[num_in_q] = sim_time;
	}

	else{
		/* Server is idle, so arriving customer has a delay of zero. */
		delay = 0.0;
		total_of_delays += delay;

		/* Increment the number of customers delayed, and make server busy. */
		++num_custs_delayed;
		server_status = BUSY;

		/* Schedule a departure (service completion). */
		time_next_event[2] = sim_time + expon(mean_service);
	}
}

void depart(void){ /*Departure event function. */
	int i;
	float delay;

	/* Check to see whether the queue is empty. */
	if(num_in_q == 0){
		/* The queue is empty so make the server idle and eliminate the
		 * departure (service completion) event from consideration. */
		server_status = IDLE;
		time_next_event[2] = 1.0e+30;
	}
	else{
		/* The queue is nonempty, so decrement the number of customers in queue. */
		--num_in_q;

		/* Compute the delay of the customer who is beginning service
		 * and update the total delay of accumulator. */
		delay = sim_time - time_arrival[1];
		total_of_delays += delay;

		/* Increment the number of customers delayed, and schedule departure. */
		++num_custs_delayed;
		time_next_event[2] = sim_time + expon(mean_service);

		/* Move each customer in queue (if any) up one place. */
		for(i = 1; i <= num_in_q; ++i){
			time_arrival[i] = time_arrival[i + 1];
		}
	}
}

std::tuple<float, float, float> report(void){ /*Report generator function */
	/* Compute and write estimates of desired measures of performance. */
	fprintf(outfile, "\nAverage delay in queue%11.3f minutes\n\n", total_of_delays / num_custs_delayed);
	fprintf(outfile, "\nAverge number in queue%10.3f\n\n", area_num_in_q / sim_time);
	fprintf(outfile, "Server utilization%15.3f\n\n", area_server_status / sim_time);
	fprintf(outfile, "total customer served %10.3f %d\n\n", area_num_in_q, num_custs_delayed);
	fprintf(outfile, "Time simulation ended%12.3f minutes", sim_time);

	float len = area_num_in_q / sim_time;
	float del = total_of_delays / num_custs_delayed;
	float util = area_server_status / sim_time;

	return std::make_tuple(len, del, util);
}

void update_time_avg_stats(void){ /* Update area accumulators for time-average statistics. */
	float time_since_last_event;

	/* Compute time since last event, and update last-event-time- marker. */
	time_since_last_event = sim_time - time_last_event;
	time_last_event = sim_time;

	/* Update area under number-in-queue function */
	area_num_in_q += num_in_q * time_since_last_event;

	/* Update area under server-busy indicator function. */
	area_server_status += server_status * time_since_last_event;
}

float expon(float mean){ /* Exponential variate generation function. */
	/* Return an exponential random variate with mean "mean". */
	return ((-mean * log(lcgrand(1))));
}
