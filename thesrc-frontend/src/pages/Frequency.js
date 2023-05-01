// Working D3 with y-Axis fixed for both charts :

// d3 both chart with mouseover: one worked, the other did not: therefore , shift to integrating two  chartistjs on a single page:
// working   version : tooltip shows on the browser  developer tool only :
import React, { useEffect, useState,useRef,useCallback } from "react";
import '../components/Chart.css';
import * as d3 from "d3";



const Frequency = (props) => {
    const dataset  = props.dataset;
    var parseTime = d3.timeParse("%Y-%m-%d %H:%M:%S");


    const [charts, setCharts] = useState([]);

    const [width, setWidth] = useState(0);
    const [height, setHeight] = useState(0);
    const lineChart = useRef();

    const [charts2, setCharts2] = useState([]);

    const [width2, setWidth2] = useState(0);
    const [height2, setHeight2] = useState(0);
    const lineChart2 = useRef();

    const drawLineHandler = useCallback((charts) => {
   
      const margin = { top: 30, right: 30, bottom: 30, left: 30 }
      setWidth(960 - margin.left - margin.right);
      setHeight( 250 - margin.top - margin.bottom);
  
      
      // set svg component
      const svg = d3.select(lineChart.current)
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        // .style("padding", 2)
        .append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);
  
      // x axis scale
      const xScale = d3.scaleTime()
      .range([margin.left, width + margin.right])
      // .range([0, width]);
      xScale.domain(d3.extent(dataset, (d) => { return d.created_at; }));
      
      const xAxis = d3.axisBottom()
      .scale(xScale);

      // append xAxis to svg
      svg.append('g').attr('class', 'x axis')
      .attr("transform", `translate(0, ${height})`)
      .call(xAxis);

      // y axis scale
      const yScale = d3.scaleLinear()
      // .range([height, 0])
      .range([height, margin.top])
      .domain([d3.min(dataset, (d) => { return d.value; }) -10, d3.max(dataset, (d) => { return d.value; }) +2]);

      // .domain([d3.min(dataset, (d) => { return d.value; }) -10, d3.max(dataset, (d) => { return d.value; }) +10]);
      // .domain([0, d3.max(dataset, (d) => { return d.value; })]);
      const yAxis = d3.axisLeft().scale(yScale);
      
      // append yAxis to svg

      svg.append('g')
      .attr('class', 'y axis')
      .call(yAxis)
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', 6)
      .attr('dy', '.71em')
      .style('text-anchor', 'end')
      .text('Voltage (V)');

      // Add tooltip
      const focus = svg.append("g")
      // .style("display", "none")
      .style("display", "all");

      focus.append("circle")
      .attr('class', 'y')
      .style('fill', 'none')
      .style('stroke', 'blue')
      .attr("r", 4.5);

      // const tooltip = d3.select(lineChart.current)
      const tooltip = d3.select(".line--content")
      .append("div")
      .style("position", "absolute")
      .attr("class", "tooltip")
      .style('opacity', 0);

      const formatTime = d3.timeFormat("%Y-%m-%d %H-%M-%S");

      
      const formatCurrency = d3.format('(.2f');

      // @ iteration 2  from the standard docs
      // :Adding the rect
      const mousemove = (event) => {
        const coordX= d3.pointer(event)[0];
        const date0 = xScale.invert(coordX);
        const bisectDate = d3.bisector( d =>  d.created_at).left;
       // const i = bisectDate(dataset, date0);
        const i = bisectDate(dataset, date0, 1);
        console.log("i is",i)
        const d0 = dataset[i - 1];
        const d1 = dataset[i];
        let d = null;
        // parseTime
        // if ((parseTime(date0) - parseTime(d0.created_at)) > (parseTime(d1.created_at) - parseTime(date0))) {

        if ((date0 - (d0.created_at)) > ((d1.created_at) - date0)) {
          d = d1;

        } else {
          d = d0;
        }

        focus.select('circle.y')
        .attr('transform', `translate(${coordX}, ${yScale(d.value)})`);
        tooltip.transition().duration(200).style('opacity', 0.9)

        console.log("d.created_at type ", typeof(d.created_at))
        tooltip.html(`<span>${d.created_at}<br/>Voltage: ${formatCurrency(d.value)}</span>`) 
        .style('left', `${coordX}px`)
        .style('top', `${(yScale(d.value)) - 28 }px`)
          ;
      };


      const line =
            d3.line()
              .x((d) => { return xScale(d.created_at); })
              .y((d) => { return yScale(d.value); })
          
       
      // just added
      const linepath = svg.append('g');


      linepath.append('path')
              .attr('class', 'line')
              .attr('d', line(dataset));

      // Draw line
      svg.append('path')
        // .datum([dataset])
        .datum(dataset)
        .attr("class", "line")
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr("d", d3.line()
          .x((d) => { return xScale(d.created_at); })
          .y((d) => { return yScale(d.value); })
        )
        ;

        // append a rect element to capture mouse events
        svg.append('rect')
        .attr('class', 'overlay')
        .attr('width', width)
        .attr('height', height)
        .style('fill', 'none')
        .style('pointer-events', 'all')
        .on('mouseover', () => focus.style('display', null))
        .on('mouseout', () => focus.style('display', 'none'))
        .on('mousemove', mousemove)
        ;

    }, [dataset, setWidth, setHeight]);

    // handler for chart 2
    const drawLineHandler2 = useCallback((charts2) => {

      const margin = { top: 30, right: 30, bottom: 30, left: 30 }
      setWidth2(960 - margin.left - margin.right);
      setHeight2( 250 - margin.top - margin.bottom);
  
      
      // set svg component
      const svg2 = d3.select(lineChart2.current)
        .attr('width', width2 + margin.left + margin.right)
        .attr('height', height2 + margin.top + margin.bottom)
        // .style("padding", 40)
        .append('g')
        .attr('transform', `translate(${margin.left}, ${margin.top})`);
  
      // x axis scale
      const xScale2 = d3.scaleTime()
      .range([margin.left, width2 + margin.right])
      // .range([0, width]);

      xScale2.domain(d3.extent(dataset, (d) => { return d.created_at; }));

      const xAxis = d3.axisBottom().scale(xScale2)
      
     // append xAxis to svg

      svg2.append('g')
      .attr('class', 'x axis')
      .attr("transform", `translate(0, ${height2})`)
      .call(xAxis);

      // y axis scale
      const yScale2 = d3.scaleLinear()
      // .range([height, 0])
      .range([height, margin.top])
      .domain([d3.min(dataset, (d) => { return d.value2; }) -80, d3.max(dataset, (d) => { return d.value2; }) +10]);
      // .domain([0, d3.max(dataset, (d) => { return d.value2; })])
      
      const yAxis = d3.axisLeft().scale(yScale2);


   
      svg2.append('g')
        .attr('class', 'y axis')
        .call(yAxis)
        .append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 6)
        .attr('dy', '.71em')
        .style('text-anchor', 'end')
        .text('Frequency (Hz)');

      // Add tooltip
     const focus2 = svg2.append("g")
        // .style("display", "none")
        .style("display", "all")

        .append("circle")
        .attr('class', 'y')
        .style('fill', 'none')
        .style('stroke', 'blue')
        .attr("r", 4.5)
        ;

   
    //  const tooltip2 = d3.select(lineChart2.current)
     const tooltip2 = d3.select(".line--content2")

    //  line--content2
        .append("div")
        .style("position", "absolute")
        .attr("class", "tooltip")
        .style('opacity', 0)
        ;

     const formatTime2 = d3.timeFormat("%Y-%m-%d %H-%M-%S");

        
     const formatCurrency2 = d3.format('(.2f');

     const mousemove = (event) => {
            const coordX2= d3.pointer(event)[0];
            const date02 = xScale2.invert(coordX2);
            const bisectDate2 = d3.bisector( d =>  d.created_at).left;
            const i2 = bisectDate2(dataset, date02, 1);
            const d02 = dataset[i2 - 1];
            const d12 = dataset[i2];
            let d = null;
            if ((date02 - (d02.created_at)) > ((d12.created_at) - date02)) {
                d = d12;

            } else {
                d = d02;
            }
            focus2.select('circle.y')
            .attr('transform', `translate(${coordX2}, ${yScale2(d.value2)})`);
            tooltip2.transition().duration(200).style('opacity', 0.9)
            // console.log("d.created_at type ", typeof(d.created_at))
            // console.log("d.created_at  ", (d.created_at))
            tooltip2.html(`<span>${d.created_at}<br/>Freq: ${formatCurrency2(d.value2)}</span>`) 
            .style('left', `${coordX2}px`)
            .style('top', `${(yScale2(d.value2) - 28)}px`);

        }

     const line2 =
            d3.line()
              .x((d) => { return xScale2(d.created_at); })
              .y((d) => { return yScale2(d.value2); })
          
      // just added
     const linepath2 = svg2.append('g');

    linepath2.append('path')
    .attr('class', 'line')
    .attr('d', line2(dataset));


        // Draw line
     svg2.append('path')
        // .datum([dataset])
        .datum(dataset)
        .attr("class", "line")
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr("d", d3.line()
        // .x((d) =>  xScale(d.created_at) )
        //   .y((d) =>  yScale(d.value) )
            .x((d) => { return xScale2(d.created_at); })
            .y((d) => { return yScale2(d.value2); })
        );
     // append a rect element to capture mouse events
     svg2.append('rect')
     .attr('class', 'overlay')
     .attr('width', width2)
     .attr('height', height2)
     .style('fill', 'none')
     .style('pointer-events', 'all')
     .on('mouseover', () => focus2.style('display', null))
     .on('mouseout', () => focus2.style('display', 'none'))
     .on('mousemove', mousemove)
     ;
        
    }, [dataset, setWidth2, setHeight2]);


    useEffect(() => {
      remove();
      removeTooltip();

  
      drawLineHandler(charts);
  
    }, [charts, drawLineHandler]);



    
    // useEfect chart 2
    useEffect(() => {
      remove2();
      removeTooltip2();
  
      drawLineHandler2(charts2);
  
    }, [charts2, drawLineHandler2]);
   
    const remove = () => {
      const g = d3.select(lineChart.current).selectAll('g');
      // check the number of existing elements, if greater than 0; remove all existing ones
      if (g.size()) {
        g.remove().exit();
      }
    };

    const removeTooltip = () => {
      const f = d3.select(".line--content").select('.tooltip');

      // const f = d3.select(".line--content").selectAll('g');
      // d3.select('#container')
      // .select('.tooltip')
      // .remove();

      // check the number of existing elements, if greater than 0; remove all existing ones
      if (f.size()) {
        f.remove().exit();
      }
    };
  
    const remove2 = () => {
      const g2 = d3.select(lineChart2.current).selectAll('g');
      // check the number of existing elements, if greater than 0; remove all existing ones
      if (g2.size()) {
        g2.remove().exit();
      }
    };

    const removeTooltip2 = () => {
      const f2 = d3.select(".line--content2").select('.tooltip');

      // const f2 = d3.select(".line--content2").selectAll('g');
      // check the number of existing elements, if greater than 0; remove all existing ones
      if (f2.size()) {
        f2.remove().exit();
      }
    };

  return (
    <div className="lines">
      <section className="line--section">
        <div id="lineContainer" className="line--container">
          <h1 className="line--title">Voltage synchrophasor</h1>
          <div className="line--content" style ={{position: "relative"}}> 
            <svg ref={lineChart}></svg>
          </div>
        </div>
      </section>

      <section className="line--section2">
        <div id="lineContainer2" className="line--container2">
          <h1 className="line--title">Frequency synchrophasor</h1>
          <div className="line--content2" style ={{position: "relative"}}>
            <svg ref={lineChart2}></svg>
          </div>
        </div>
      </section>
    </div>
  
  );
}

export default Frequency;