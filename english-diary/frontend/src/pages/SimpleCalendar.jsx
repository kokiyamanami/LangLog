/**
 * SimpleCalendar - シンプルなカレンダーコンポーネント
 * 日曜日始まり、7列 × 6行のグリッド表示
 */

/**
 * カレンダーセル配列を生成するヘルパー関数
 */
function generateCalendarDays(year, month) {
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startDayOfWeek = firstDay.getDay()
  const daysInMonth = lastDay.getDate()
  const prevMonthLastDay = new Date(year, month, 0).getDate()

  const days = []

  // 前月の日付
  for (let i = startDayOfWeek - 1; i >= 0; i--) {
    days.push({
      date: new Date(year, month - 1, prevMonthLastDay - i),
      isCurrentMonth: false,
      day: prevMonthLastDay - i
    })
  }

  // 現在の月の日付
  for (let i = 1; i <= daysInMonth; i++) {
    days.push({
      date: new Date(year, month, i),
      isCurrentMonth: true,
      day: i
    })
  }

  // 翌月の日付（6行 × 7列 = 42セルを埋める）
  const remaining = 42 - days.length
  for (let i = 1; i <= remaining; i++) {
    days.push({
      date: new Date(year, month + 1, i),
      isCurrentMonth: false,
      day: i
    })
  }

  return days
}

/**
 * 日付セル表示コンポーネント
 */
function CalendarCell({ dayObj, tileClassName, tileContent, onClickDay }) {
  const { date, isCurrentMonth, day } = dayObj
  const className = isCurrentMonth ? tileClassName({ date }) : 'other-month'
  const content = isCurrentMonth ? tileContent(date) : null
  const isClickable = isCurrentMonth

  return (
    <div
      className={`calendar-cell ${className}`}
      onClick={() => isClickable && onClickDay(date)}
      style={{
        cursor: isClickable ? 'pointer' : 'default',
        opacity: isClickable ? 1 : 0.4
      }}
    >
      <div className="day-number">{day}</div>
      {content && <div className="day-content">{content}</div>}
    </div>
  )
}

export function SimpleCalendar({ value, onClickDay, tileContent, tileClassName }) {
  const year = value.getFullYear()
  const month = value.getMonth()
  const days = generateCalendarDays(year, month)
  const weekdays = ['日', '月', '火', '水', '木', '金', '土']

  return (
    <div className="simple-calendar">
      <div className="calendar-header-simple">
        <h3>{year}年{month + 1}月</h3>
      </div>

      <div className="calendar-weekdays">
        {weekdays.map((day) => (
          <div key={day} className="weekday-header">
            {day}
          </div>
        ))}
      </div>

      <div className="calendar-grid">
        {days.map((dayObj, idx) => (
          <CalendarCell
            key={idx}
            dayObj={dayObj}
            tileClassName={tileClassName}
            tileContent={tileContent}
            onClickDay={onClickDay}
          />
        ))}
      </div>
    </div>
  )
}
