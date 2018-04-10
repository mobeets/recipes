---
---

// https://kamisama.github.io/cal-heatmap/#domainDynamicDimension
var data = {{ site.data.books | jsonify }};

function parser(data) {
    var stats = {};
    for (var d in data) {
        for (var e in data[d]) {
            dt = Date.parse(data[d][e].start_date)/1000;
            console.log(data[d][e]);
            if (!(dt in stats)) {
                stats[dt] = 0;
            }
            stats[dt] += 1;
        }
    }
    return stats;
}

var cal = new CalHeatMap();
cal.init({
    data: data,
    afterLoadData: parser,
    start: new Date(2015, 0),
    domain: "month",
    subDomain: "x_week",
    // domainLabelFormat: "%Y-%b",
    range: 12,
    // rowLimit: 5,
    // legend: [500, 1000, 1500, 2000, 3000, 4000],
    browsing: true,
    domainGutter: 8,
    cellSize: 15,
    cellPadding: 2,
    cellRadius: 4,
    displayLegend: false,
    // domainDynamicDimension: false,
    domainLabelFormat: "%b",
    legendColors: {
        // min: "#eeeeee",
        // max: "blue",
        empty: "white"
        // Will use the CSS for the missing keys
    },
    label: {
        position: "top",
        // width: 46,
        // rotate: "left"
    },
    // subDomainTextFormat: "%d",
    previousSelector: "#prevButton",
    nextSelector: "#nextButton",
    onClick: function(date, nb) {
        $("#info").html("You just clicked <br/>on <b>" +
            date + "</b> <br/>with <b>" +
            (nb === null ? "unknown" : nb) + "</b> items"
        );
    }
});
