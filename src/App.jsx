import { useState, useEffect } from 'react'
import React from 'react';
import Week from './components/calendar_week.jsx'
import "./style/app_style.css"

function App() {

    const [calendar, setCalendar] = useState(0)

    useEffect(() => {
        fetch('/api/calendar').then(res => res.json()).then(text => {
            const data = JSON.parse(text);
            setCalendar(data)
        });
    }, []);
    
    return (
        <main>
            <div className="calendar-container">
                <nav>Placeholder</nav>
                <Week weekNum={33} calendar={calendar}/>
            </div>
        </main>
    )

}

export default App
