<template>
    <v-container>
        <v-row justify="center">
            <v-col>
                <v-text-field v-model="start" label="Start date" type="Date" density="compact" variant="solo-inverted"
                    class="mr-5" style="max-width: 200px;" Flat></v-text-field>
                <v-text-field v-model="end" label="End date" type="Date" density="compact" variant="solo-inverted"
                    style="max-width: 200px;" Flat></v-text-field>
                <v-spacer></v-spacer>
                <v-btn class="text-caption" @click="updateLineCharts(); updateScatterPlot(); updateCard();" text="Analyze"></v-btn>
            </v-col>
            <v-col align="center">
                <v-card class="mb-5" width="350" color="surface" title="Average" subtitle="For the selected period">
                    <v-card-item align="center">
                        <span class="text-h1">{{ reserve.avg }}</span>
                        <small>Gal</small>
                    </v-card-item>
                </v-card>
            </v-col>
            <v-col></v-col>
            <v-col></v-col>
        </v-row>
        <v-row class="row2" justify="center" max-width="1200">
            <v-col class="col1" cols="9">
                <figure class="highcharts-figure">
                    <div id="container1"></div>
                </figure>
            </v-col>
        </v-row>
        <v-row class="row2" justify="center" max-width="1200">
            <v-col class="col1" cols="9">
                <figure class="highcharts-figure">
                    <div id="container2"></div>
                </figure>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
/** JAVASCRIPT HERE */

// IMPORTS
import { ref, reactive, watch, onMounted, onBeforeUnmount, computed } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useMqttStore } from '@/store/mqttStore'; // Import Mqtt Store
import { storeToRefs } from "pinia";

import { useAppStore } from "@/store/appStore";


// Highcharts, Load the exporting module and Initialize exporting module.
import Highcharts from 'highcharts';
import more from 'highcharts/highcharts-more';
import Exporting from 'highcharts/modules/exporting';
Exporting(Highcharts);
more(Highcharts);



// VARIABLES
const router = useRouter();
const route = useRoute();

const AppStore = useAppStore();

const Mqtt = useMqttStore();
const { payload, payloadTopic } = storeToRefs(Mqtt);

const start = ref("");
const end = ref("");

const reserve = reactive({ "avg": 0 })

const WaterReserve = ref(null); // Chart object
const ScatterPlot = ref(null); // Chart object


// FUNCTIONS
const CreateCharts = async () => {
    // TEMPERATURE CHART
    WaterReserve.value = Highcharts.chart('container1', {
        chart: { zoomType: 'x' },
        title: { text: 'Water Management Analysis', align: 'left' },
        yAxis: {
            title: { text: 'Water Reserve', style: { color: '#000000' } },
            labels: { format: '{value} Gal' }
        },
        xAxis: {
            type: 'datetime',
            title: { text: 'Time', style: { color: '#000000' } },
        },
        tooltip: { shared: true, },
        series: [
            {
                name: 'Reserve',
                type: 'spline',
                data: [],
                turboThreshold: 0,
                color: Highcharts.getOptions().colors[0]
            },
        ],
    });
    ScatterPlot.value = Highcharts.chart('container2', {
        chart: { zoomType: 'x' },
        title: { text: 'Height and Water Level Correlation Analysis', align: 'left' },
        yAxis: {
            title: { text: 'Height', style: { color: '#000000' } },
            labels: { format: '{value} in' }
        },
        xAxis: {
            title: { text: 'Water Height', style: { color: '#000000' } },
            labels: { format: '{value} in' }
        },
        tooltip: { pointFormat: 'Water Height: {point.x} in <br/> Height: {point.y} in' },
        series: [
            {
                name: 'Analysis',
                type: 'scatter',
                data: [],
                turboThreshold: 0,
                color: Highcharts.getOptions().colors[0]
            },
        ],
    });
};

const updateLineCharts = async () => {
    if (!!start.value && !!end.value) {
        // Convert output from Textfield components to 10 digit timestamps
        let startDate = new Date(start.value).getTime() / 1000;
        let endDate = new Date(end.value).getTime() / 1000;
        // Fetch data from backend
        const data = await AppStore.getAllInRange(startDate, endDate);
        // Create arrays for each plot 
        let reserve = [];
        // Iterate through data variable and transform object to format recognized by highcharts
        data.forEach(row => {
            reserve.push({ "x": row.timestamp * 1000, "y": parseFloat(row.reserve.toFixed(0)) });
           
        });
        // Add data to Temperature and Heat Index chart
        WaterReserve.value.series[0].setData(reserve);
        
    }
}

const updateScatterPlot = async () => {
    if (!!start.value && !!end.value) {
        // Convert output from Textfield components to 10 digit timestamps
        let startDate = new Date(start.value).getTime() / 1000;
        let endDate = new Date(end.value).getTime() / 1000;
        // Fetch data from backend
        const data = await AppStore.getAllInRange(startDate, endDate);
        // Create arrays for each plot 
        let points = [];
        

        // Iterate through data variable and transform object to format recognized by highcharts
        data.forEach(row => {
            points.push({ "x": parseFloat(row.waterheight.toFixed(0)), "y": parseFloat(row.radar.toFixed(0)) });
           });
        // Add data to Temperature and Heat Index chart
        ScatterPlot.value.series[0].setData(points);
        

    }
}

const updateCard = async () => {
    // Retrieve Min, Max, Avg, Spread/Range
    if (!!start.value && !!end.value) {
        // 1. Convert start and end dates collected fron TextFields to 10 digit timestamps
        let startDate = new Date(start.value).getTime() / 1000;
        let endDate = new Date(end.value).getTime() / 1000;

        // 2. Fetch data from backend by calling the API functions
        const ReserveAVGfromDatabase = await AppStore.getReserveAVG(startDate, endDate);
        console.log(ReserveAVGfromDatabase)

        //3. complete for min, avg and range
        //4. complete max, min, avg and range for the humidity variable
        
        reserve.avg = ReserveAVGfromDatabase[0].average.toFixed(1);
    }
}

onMounted(() => {
    // THIS FUNCTION IS CALLED AFTER THIS COMPONENT HAS BEEN MOUNTED 
    CreateCharts();
    Mqtt.connect(); // Connect to Broker located on the backend
    setTimeout(() => {
        // Subscribe to each topic
        Mqtt.subscribe("620142646");
        Mqtt.subscribe("topic2");
    }, 3000);
});



onBeforeUnmount(() => {
    // THIS FUNCTION IS CALLED RIGHT BEFORE THIS COMPONENT IS UNMOUNTED
    Mqtt.unsubcribeAll();

});


</script>


<style scoped>
/** CSS STYLE HERE */
Figure {
    border: 2px solid black;
}
</style>