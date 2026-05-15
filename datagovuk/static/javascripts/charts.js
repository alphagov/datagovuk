(function () {
    'use strict';

    /**
     * Function responsible for handling the chart loading and everything else attached to it (e.g. loading the font used in the chart before showing it, etc.)
     * @param {HTMLCanvasElement} canvasElement - The canvas element of the chart
     * @returns {Promise<{initialise: function(): *, loadChart: function(): *}>}>} An object with methods to initialise and load the chart
     */
    async function chartHandler(canvasElement) {

        // FIRST assign the necessary properties...
        const properties = {
            canvasElement: canvasElement,
            canvasContainer: canvasElement.parentNode,
            chartInstance: window.Chartkick.charts[canvasElement.parentNode.id]
        };

        // THEN load the font used in the chart...
        properties.canvasContainer.style.opacity = 0;
        await document.fonts.load("15px Inter, sans-serif");

        return {
            initialise() {
                if (!properties.chartInstance)
                    throw new Error("It could not find Chartkick chart instance for canvas element");

                return this;
            },

            loadChart() {
                const chart = properties.chartInstance.getChartObject();
                properties.chartInstance.getChartObject().update();
                properties.canvasContainer.style.opacity = 1;

                return this;
            },
        }
    }


    /**
     * Function responsible for starting the chart handler
     */
    function start() {
        const chart = ['.bar-chart', '.line-chart'].map(selector => document.querySelector(selector)).find(Boolean);
        if (!chart) return;

        const canvas = chart.querySelector('canvas');
        if (!canvas) return;

        (async () => {
            try {
                const handler = await chartHandler(canvas);
                await handler.initialise().loadChart();
            } catch (error) {
                console.error("Error in chartHandler because:", error);
            }
        })();
    }

    // Start the chart handler once the page has loaded
    start();
}());
