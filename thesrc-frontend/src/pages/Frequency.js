import React, { useState , useEffect} from 'react';
import axios from 'axios';
import * as d3 from "d3";

import { Line } from 'react-chartjs-2';
import { Chart as ChartJS, Title, Tooltip, LineElement, Legend, CategoryScale, LinearScale, PointElement, Filler } from 'chart.js';

ChartJS.register(Title, Tooltip, LineElement, Legend, CategoryScale, LinearScale, PointElement, Filler);

export default function Frequency() {
  const [data, setData] = useState([]);
  // const [data1, setData1] = useState([]);

  const [myGraph, setMyGraph] = useState({
    labels: [],
    datasets: [
      {
        label: "pmu synchrophasor frequency",
        data: [],
        backgroundColor: 'black',
        borderColor: 'red',
        tension: 0.4,
        fill: false,
        pointStyle: 'star',
        pointBorderColor: 'blue',
        pointBackgroundColor: '#fff'
      }
    ]
  });
  

  const getData = async () => {
    const { data } = await axios.get(`http://localhost:8000/chart/`);
    setData(data);
    setMyGraph({
      labels: data.map((item) => item.created_at),
      datasets: [
        {
          label: "pmu synchrophasor voltage",
          data: data.map((item) => item.mag),
          backgroundColor: 'black',
          borderColor: 'red',
          tension: 0.4,
          fill: false,
          pointStyle: 'circle',
          pointBorderColor: 'red',
          pointBackgroundColor: '#fff'
        }
      ]
    });
  };

  useEffect(() => {
    getData();
  }, 
  []);
  

  return (
    <div className= 'page' style={{width:'200', height:'50'}}>
      <Line data={myGraph} />
    </div>
  
  );
}