<template>
    <v-container class="container" color="surface" flat align="center">
        <v-row>
            <v-col cols="12">
                <v-card title="Combination" subtitle="Enter your four digit passcode" align="center">
                    <v-sheet color="surface">
                        <v-otp-input v-model="passcode" length="4"></v-otp-input>
                    </v-sheet>
                </v-card><br>

                <v-btn color="primary" @click="SubmitPasscode();" >Submit</v-btn>
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
const AppStore = useAppStore(); 


// VARIABLES
const router = useRouter();
const route = useRoute();
const Mqtt = useMqttStore();
const { payload, payloadTopic } = storeToRefs(Mqtt);
var passcode = ref("0");

// FUNCTIONS
onMounted(() => {
    // THIS FUNCTION IS CALLED AFTER THIS COMPONENT HAS BEEN MOUNTED
    Mqtt.connect(); // Connect to Broker located on the backend
    setTimeout(() => {
        // Subscribe to each topic
        Mqtt.subscribe("620142646");
        Mqtt.subscribe("620142646_sub");
    }, 3000);
});




onBeforeUnmount(() => {
    // THIS FUNCTION IS CALLED RIGHT BEFORE THIS COMPONENT IS UNMOUNTED
    Mqtt.unsubcribeAll();
});

const SubmitPasscode = async () => {
  const post = await AppStore.SetCombination(passcode.value);
};

</script>


<style scoped>
/** CSS STYLE HERE */
</style>