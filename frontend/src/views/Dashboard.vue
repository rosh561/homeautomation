<template>
    <v-container fluid align="center">
        <v-row class="row1" max-width="1200">
            <v-col class="col1" cols="1">
                <v-sheet class="pa-2" height="370">
                    <v-slider v-model="Waterheight" color="green" readonly label="Height (in)" direction="vertical"
                        thumb-label="always" :max="94.5" :min="0" track-size="50"></v-slider>
                </v-sheet>
            </v-col>
            <v-col class="col2" cols="11">
                <v-sheet class="pa-2">
                    <figure class="highcharts-figure">
                        <div id="container"></div>
                    </figure>
                </v-sheet>
            </v-col>
        </v-row>
        <v-row class="row2" max-width="1200">
            <v-col class="col1" cols="8">
                <v-sheet class="pa-2">
                    <figure class="highcharts-figure">
                        <div id="container0"></div>
                    </figure>
                </v-sheet>
            </v-col>
            <v-col class="col2" cols="4">
                <v-sheet class="pa-2">
                    <v-card title="Water Level" subtitle="Capacity Remaining" align="center">

                        <div id="fluid-meter"></div>
                        <v-dialog v-model="dialog" width="500">
                            <v-card color="purple" max-width="400" title="Overflow Detected"
                                text="The tank is overflowing.">
                            </v-card>
                        </v-dialog>
                    </v-card>
                </v-sheet>
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

// Highcharts, Load the exporting module and Initialize exporting module.
import Highcharts from 'highcharts';
import more from 'highcharts/highcharts-more';
import Exporting from 'highcharts/modules/exporting';
Exporting(Highcharts);
more(Highcharts);


// VARIABLES
const router = useRouter();
const route = useRoute();

const Mqtt = useMqttStore();
const { payload, payloadTopic } = storeToRefs(Mqtt);

const points = ref(600); // Specify the quantity of points to be shown on the live graph simultaneously.
const shift = ref(false); // Delete a point from the left side and append a new point to the right side of the graph.
const dialog = ref(false);
const WaterReservesAreaGraph = ref(null); // Chart object
const GaugeGraph = ref(null); // Chart object

var fm = new FluidMeter();

const Waterheight = ref(50)

/*let dialog = false;
if (Percentage > 100) {
    dialog = true;
}
else {
    dialog = false;
}*/


// FUNCTIONS
const CreateCharts = async () => {
    // TEMPERATURE CHART
    WaterReservesAreaGraph.value = Highcharts.chart('container', {
        chart: { zoomType: 'x' },
        title: { text: 'Water Reserves(10 min)', align: 'left' },
        yAxis: {
            title: { text: 'Water Level', style: { color: '#000000' } },
            labels: { format: '{value} Gal' }
        },
        xAxis: {
            type: 'datetime',
            title: { text: 'Time', style: { color: '#000000' } },
        },
        tooltip: { shared: true, },
        series: [
            {
                name: 'Water',
                type: 'area',
                data: [],
                turboThreshold: 0,
                color: Highcharts.getOptions().colors[0]
            },
        ],
    });

    // GAUGE GRAPH
    GaugeGraph.value = Highcharts.chart('container0', {
        title: { text: 'Water Reserves', align: 'left' },
        // the value axis
        yAxis: {
            min: 0,
            max: 1000,
            tickPixelInterval: 72,
            tickPosition: 'inside',
            tickColor: Highcharts.defaultOptions.chart.backgroundColor || '#FFFFFF',
            tickLength: 20,
            tickWidth: 2,
            minorTickInterval: null,
            labels: { distance: 20, style: { fontSize: '14px' } },
            lineWidth: 0,
            plotBands: [{ from: 0, to: 200, color: '#DF5353', thickness: 20 }, {
                from: 200, to: 600, color: '#DDDF0D', thickness: 20
            }, { from: 600, to: 1000, color: '#55BF3B', thickness: 20 }]
        },
        tooltip: { shared: true, },
        pane: { startAngle: -90, endAngle: 89.9, background: null, center: ['50%', '75%'], size: '110%' },
        series: [{
            type: 'gauge',
            name: 'Water Capacity',
            data: [],
            tooltip: { valueSuffix: ' Gal' },
            dataLabels: {
                format: '{y} Gal', borderWidth: 0, color: (Highcharts.defaultOptions.title &&
                    Highcharts.defaultOptions.title.style && Highcharts.defaultOptions.title.style.color) || '#333333', style: { fontSize: '16px' }
            },
            dial: { radius: '80%', backgroundColor: 'gray', baseWidth: 12, baseLength: '0%', rearLength: '0%' },
            pivot: { backgroundColor: 'gray', radius: 6 }
        }]
    });

    fm.init({
        targetContainer: document.getElementById("fluid-meter"),
        fillPercentage: 0,
        options: {
            fontSize: "70px",
            fontFamily: "Arial",
            fontFillStyle: "white",
            drawShadow: true,
            drawText: true,
            drawPercentageSign: true,
            drawBubbles: true,
            size: 300,
            borderWidth: 25,
            backgroundColor: "#e2e2e2",
            foregroundColor: "#fafafa",
            foregroundFluidLayer: {
                fillStyle: "purple",
                angularSpeed: 100,
                maxAmplitude: 12,
                frequency: 30,
                horizontalSpeed: -150
            },
            backgroundFluidLayer: {
                fillStyle: "pink",
                angularSpeed: 100,
                maxAmplitude: 9,
                frequency: 30,
                horizontalSpeed: 150
            }
        }
    });
};

// WATCHERS
watch(payload, (data) => {
    Waterheight.value = data.waterheight;
    fm.setPercentage(data.percentage);
    if (data.percentage > 100) {
        dialog.value = true;
    } else {
        dialog.value = false;
    }
    if (points.value > 0) { points.value--; }
    else { shift.value = true; }
    WaterReservesAreaGraph.value.series[0].addPoint({ y: parseFloat(data.reserve.toFixed(0)), x: data.timestamp * 1000 },
        true, shift.value);
    GaugeGraph.value.series[0].points[0].update(parseFloat(data.reserve));


})

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