import "../style/week_style.css"
import * as dateUtil from "../utils/date_time.ts"

const Week = ({weekNum, calendar}) => {

    const weekDays = ["Mon", "Tis", "Ons", "Tor", "Fre", "Lör", "Sön"]

    let weekStart = dateUtil.getDateOfIsoWeek(weekNum, 2025)
    let weekEnd = weekStart.addDays(7)
    let weekDates = dateUtil.getDates(weekStart, weekEnd)


    const dayList = weekDates.map((dateObj, index) => {
        const formatted = dateUtil.formatDate(dateObj);

        if (calendar[formatted]){
            
            let dayItem = calendar[formatted].map((activity) => {
                return(
                    <div className="activity-container">
                        
                        <h3>{activity["title"]}</h3>
                        <p>Start tid: {activity["start_time"]}</p>
                        <p>Slut tid: {activity["end_time"]}</p>
                        <p>Längd: {activity["duration"]}</p>
                        <p>Antekningar: {activity["notes"]}</p>
                        <p>Tagg: {activity["tag"]}</p>
                    </div>
                )   
            })

            return (
                <div className="day-container scroll">
                    <h1>{weekDays[index]}</h1>
                    {dayItem}
                </div>
            )
        }
        else {
            return (<div className="day-container">
                <h1>{weekDays[index]}</h1>
            </div>)
        }
    });

    return ( 
        <>
            <div className="week-container">
                {dayList}
            </div>

        </>
    )
}


export default Week;