import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';


export default class AutomationGraph extends React.PureComponent {

  constructor(props) {
    super(props);
    this.state = {
      data: [],
    };
  }

  componentDidMount() { }

  componentWillUnmount() { }

  componentDidUpdate(prevProps, prevState) {
    const { readings, feed_delivered, feed_rate, phase_elapsed_time } = this.props.automation;

    if (this.props.automation.phase_elapsed_time && prevProps.automation.phase_elapsed_time && this.props.automation.phase_elapsed_time > prevProps.automation.phase_elapsed_time) {
      const values = {
        elapsedTime: parseFloat((phase_elapsed_time / 60).toFixed(2)),
        feedDelivered: parseFloat(feed_delivered.toFixed(2)),
        feedRate: parseFloat(feed_rate.toFixed(2)),
        vacuumPSI: readings['supply_pump_vacuum_pressure'],
        outletPSI: readings['delivery_pump_outlet_pressure']
      }

      this.setState({ data: [...this.state.data, values] });
    }
  }

  renderMainGraphs() {
    const { data } = this.state;
    const CustomTooltip = ({ active, payload, label }) => {
      if (active && payload && payload.length) {
        return (
          <div className="tooltip">
            <div>Elapsed Time: {label} mins</div>
            <div className="label">Feed Delivered: {payload[0].value} kg</div>
            <div className="label">Feed Rate: {payload[1].value} kg/m</div>
          </div>
        );
      }
      return null;
    };

    return (
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          key={data.length}
        >
          <CartesianGrid strokeDasharray="4 4" strokeOpacity={0.4} />
          <XAxis dataKey="elapsedTime" />
          <YAxis
            yAxisId="left"
            orientation="left"
          />
          <YAxis
            yAxisId="right"
            orientation="right"
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            animationDuration={0}
            strokeWidth={2}
            name="Feed Delivered (kg)"
            dataKey="feedDelivered"
            stroke="#ed6c02"
            dot={null}
            yAxisId="left"
          />
          <Line
            type="monotone"
            animationDuration={0}
            strokeWidth={2}
            name="Feed Rate (kg/m)"
            dataKey="feedRate"
            stroke="#1976d2"
            dot={null}
            yAxisId="right"
          />
        </LineChart>
      </ResponsiveContainer>
    )
  }

  render() {
    const { readings } = this.props.automation;
    return (
      <div className='automation__graph'>
        PSI: {readings['supply_pump_vacuum_pressure']}
        {this.renderMainGraphs()}
      </div>
    )
  }

}

