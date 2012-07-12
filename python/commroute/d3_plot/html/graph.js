
d3.json("graph.json", function(json) {

    var links = json.links;
    var nodes = json.nodes;

    var w = 960,
        h = 500;

    var tick = function() {
        path.attr("d", function(d) {
            var dx = d.target.x - d.source.x,
                dy = d.target.y - d.source.y,
                dr = Math.sqrt(dx * dx + dy * dy);
            return "M" + d.source.x + "," + d.source.y + "A" + dr + "," + dr + " 0 0,1 " + d.target.x + "," + d.target.y;
        });

        circle.attr("transform", function(d) {
            return "translate(" + d.x + "," + d.y + ")";
        });

        text.attr("transform", function(d) {
            return "translate(" + d.x + "," + d.y + ")";
        });

        edge_text.attr("transform", function(d) {
            return "translate(" + .5*(d.source.x + d.target.x) + "," + .5*(d.source.y + d.target.y) + ")";
        });

    };

    var force = d3.layout.force()
        .nodes(nodes)
        .links(links)
        .size([w, h])
        .friction(.001)
        .linkDistance(function(d) {return d.value/10.;})
        .charge(10)
        .on("tick", tick)
        .start();

    var svg = d3.select("body").append("svg:svg")
        .attr("width", w)
        .attr("height", h);

// Per-type markers, as they don't inherit styles.
    svg.append("svg:defs")
        .append("svg:marker")
        .attr("id","marker")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 15)
        .attr("refY", -1.5)
        .attr("markerWidth", 6)
        .attr("markerHeight", 6)
        .attr("orient", "auto")
        .append("svg:path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("class", "marker");


    var path = svg.append("svg:g").selectAll("path")
        .data(force.links())
        .enter().append("svg:path")
//    .attr("stroke-width", function(d){return d.value;})
        .attr("marker-end", "url(marker#marker)");

    var circle = svg.append("svg:g").selectAll("circle")
        .data(force.nodes())
        .enter().append("svg:circle")
        .attr("r", 6)
        .call(force.drag);

    var text = svg.append("svg:g").selectAll("g")
        .data(force.nodes())
        .enter().append("svg:g");


    text.append("svg:text")
        .attr("x", 8)
        .attr("y", ".31em")
        .attr("class", "shadow")
        .text(function(d) { return d.name; });

    text.append("svg:text")
        .attr("x", 8)
        .attr("y", ".31em")
        .text(function(d) { return d.name; });

    var edge_text = svg.append("svg:g").selectAll("g")
        .data(force.links())
        .enter()
        .append("svg:g");

    edge_text.append("svg:text")
        .attr("x", 8)
        .attr("y",".31em")
        .attr("class", "shadow")
        .text(function(d) { return d.attrs.name; });

    edge_text.append("svg:text")
        .attr("x", 8)
        .attr("y",".31em")
        .text(function(d) { return d.attrs.name; });

});


