import { defineStore } from 'pinia'
import { ref } from 'vue'


export const useAppStore = defineStore('app', () => {

    /*  
    The composition API way of defining a Pinia store
    ref() s become state properties
    computed() s become getters
    function() s become actions  
    */

    // STATES 



    // ACTIONS
    const getAllInRange = async (start, end) => {
        // FETCH REQUEST WILL TIMEOUT AFTER 20 SECONDS 
        const controller = new AbortController();
        const signal = controller.signal;
        const id = setTimeout(() => { controller.abort() }, 60000);
        const URL = `/api/reserve/${start}/${end}`;
        try {
            const response = await fetch(URL, { method: 'GET', signal: signal });
            if (response.ok) {
                const data = await response.json();
                let keys = Object.keys(data);
                if (keys.includes("status")) {
                    if (data["status"] == "found") {
                        // console.log(data["data"] ) 
                        return data["data"];
                    }
                    if (data["status"] == "failed"
                    ) {
                        console.log("getAllInRange returned no data");
                    }
                }
            }
            else {
                const data = await response.text();
                console.log(data);
            }
        }
        catch (err) {
            console.error('getAllInRange error: ', err.message);
        }
        return []
    }

    const getReserveAVG = async (start, end) => {
        // FETCH REQUEST WILL TIMEOUT AFTER 20 SECONDS 
        const controller = new AbortController();
        const signal = controller.signal;
        const id = setTimeout(() => { controller.abort() }, 60000);
        const URL = `/api/avg/${start}/${end}`;
        try {
            const response = await fetch(URL, { method: 'GET', signal: signal });
            if (response.ok) {
                const data = await response.json();
                let keys = Object.keys(data);
                if (keys.includes("status")) {
                    if (data["status"] == "found") {
                        // console.log(data["data"] ) 
                        return data["data"];
                    }
                    if (data["status"] == "failed"
                    ) {
                        console.log("getReserveAVG returned no data");
                    }
                }
            }
            else {
                const data = await response.text();
                console.log(data);
            }
        }
        catch (err) {
            console.error('getReserveAVG error: ', err.message);
        }
        return []
    }

    const SetCombination = async (passcode) => {
        // FETCH REQUEST WILL TIMEOUT AFTER 20 SECONDS
        //console.log(passcode);
        const controller = new AbortController();
        const signal = controller.signal;
        const id = setTimeout(() => { controller.abort() }, 60000);
        const form = new FormData(); //Create Form Object
        form.append("passcode", passcode); // Save passcode to form object
        console.log(form)
        const URL = `/api/set/combination`;
        try {
            const response = await fetch(URL, { method: 'POST', signal: signal, body: form,});
            if (response.ok) {
                const data = await response.json();
                let keys = Object.keys(data);
                if (keys.includes("status")) {
                    if (data["status"] == "complete") {
                        //console.log(data["data"]);
                        return data["data"];
                    }
                    if (data["status"] == "failed"
                    ) {
                        console.log("SetCombination returned no data");
                    }
                }
            }
            else {
                const data = await response.text();
                console.log(data);
            }
        }
        catch (err) {
            console.error('SetCombination error: ', err.message);
        }
        return []
    }




    return {
        // EXPORTS	
        getAllInRange,
        getReserveAVG,
        SetCombination


    }
}, { persist: true });