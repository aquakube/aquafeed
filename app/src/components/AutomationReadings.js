import React from 'react';
import HardwareFeedback from './HardwareFeedback';

export default class AutomationReadings extends React.PureComponent {

  constructor(props) {
    super(props);
    this.state = {
      rows: [],
      readings: {}
    };
  }

  componentDidMount() { }

  componentWillUnmount() { }

  componentDidUpdate(prevProps, prevState) {
    const { context, data } = this.props.cloudevent; 
    const { readings } = data;
    const prevTime = new Date(prevProps.cloudevent?.context?.timestamp).getTime();
    const currTime = new Date(context.timestamp).getTime();
    if (currTime > prevTime) {
      const rows = [];
      for (const [key, value] of Object.entries(readings)) {
        rows.push({'name': key, 'value': value});
      }

      this.setState({ rows: rows, readings: readings});
    }
  }

  render() {
    const { rows, readings } = this.state

    return (
      <div className="automation_readings">
        <HardwareFeedback
          title="Supply Pump"
          speedDemanded={readings['usersupplypumpspeeddemand']}
          speedFeedback={readings['supplypumpspeedfeedback']}
          isRunning={readings['userrunsupplypump']}
          pressure={readings['supplypumpvacuumsensor']}
          displayPressure={true}
          color="primary"
          >
        </HardwareFeedback>
        <HardwareFeedback
          title="Delivery Pump"
          speedDemanded={readings['userdeliverypumpspeeddemand']}
          speedFeedback={readings['deliverypumpspeedfeedback']}
          isRunning={readings['userrundeliverypump']}
          pressure={readings['deliverypumpoutletpressure']}
          displayPressure={true}
          color="primary"
          >
        </HardwareFeedback>
        <HardwareFeedback
          title="Auger"
          speedDemanded={readings['useraugermotorspeeddemand']}
          speedFeedback={readings['augermotorspeedfeedback']}
          isRunning={readings['userrunaugermotor']}
          color="primary"
          >
        </HardwareFeedback>
      </div>
    );
  }

}
