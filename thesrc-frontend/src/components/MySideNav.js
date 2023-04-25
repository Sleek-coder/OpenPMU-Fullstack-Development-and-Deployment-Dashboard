import SideNav, {Toggle, NavItem, NavIcon, NavText} 
from "@trendmicro/react-sidenav";
import  "@trendmicro/react-sidenav/dist/react-sidenav.css";
import { useNavigate } from 'react-router-dom';
import Logo from '../assets/CMU.png';

// function MySideNav() {
const MySideNav = (props) => {
    // console.log("props from sideNav is", props)
    const dataset = props.dataset;
    // console.log("dataset from SideNav is", dataset)

    {/* <img  src={Logo} className="logo" /> */}

    const navigate = useNavigate();
    return <SideNav onSelect={selected=> {console.log(selected); navigate('/'+ selected)}}
        className='mysidenav'
        > 
        <SideNav.Toggle />
        <SideNav.Nav defaultSelected="voltage">
            <img  src={Logo} className="logo" />



            <NavItem eventKey="voltage">
                <NavIcon>
                    <i className='fa fa-fw fa-home' style={{fontSize: '1.5em' }}></i>
                </NavIcon>
                <NavText style={{'color': 'white',
                       'fontSize': 15}}>
                    Voltage
                </NavText>
            </NavItem>

            {/* <NavItem eventKey="chart">
                <NavIcon>
                    <i className='fa-solid fa-gear' style={{fontSize: '1.5em' }}></i>
                </NavIcon>
                <NavText>
                    Chart
                </NavText>
            </NavItem> */}

            <NavItem eventKey="frequency">
                <NavIcon>
                    <i className='fa-solid fa-gear' style={{fontSize: '1.5em' }}></i>
                </NavIcon>
                <NavText style={{'color': 'white',
                       'fontSize': 15}}>
                    Frequency
                </NavText>
            </NavItem>


        </SideNav.Nav>
        </SideNav>

function receiveData(){

}

}

export default MySideNav;