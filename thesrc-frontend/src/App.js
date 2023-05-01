import './App.css';
import MySideNav from './components/MySideNav';
import Navbar from './components/Navbar';

import Voltage from './pages/Voltage';
import Frequency from './pages/Frequency';



import  { BrowserRouter  as Router, Routes, Route} from 'react-router-dom';
import React, { useEffect, useState,useRef } from "react";
import axios from 'axios';
import * as d3 from "d3";




// export default function App() {
const App = ()  =>{

  const [dataset, setDataset] = useState([]);
  const getData = async () => {
    const { data }   = await axios.get(`http://localhost:8000/chart/`);
    var parseTime = d3.timeParse("%Y-%m-%d %H:%M:%S");

    data.map((d,i) => {

      d.id = i; 
      d.created_at = parseTime(d.created_at);
      d.value = +d.mag;
      d.value2 = +d.freq;


    });
    setDataset(data);

  }
  useEffect(() => {
    // let interval = 
    // setInterval(() => {

    //   getData()
    // }, 1);

  getData();

  }, []);
        



  return (
    <Router>
     <Navbar/>

        {/* <MySideNav dataset ={dataset}/> */}
          <Routes>
            <Route path='/' element={<Frequency dataset= {dataset}/>} />

            {/* <Route path='/voltage' element={<Voltage/>} /> */}
            {/* <Route path='/chart' element={<Chart/>} /> */}
          </Routes>
    </Router>
  );
}
export default  App;
