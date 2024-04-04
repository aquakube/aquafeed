
import React from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Card,
  CardContent,
  LinearProgress,
  Stack,
  Typography
} from '@mui/material';

export default class HardwareFeedback extends React.PureComponent {

  constructor(props) {
    super(props);
    this.state = { };
  }

  componentDidMount() { }

  componentWillUnmount() { }

  componentDidUpdate(prevProps, prevState) { }

  backgroundColor(isRunning) {
    if (isRunning === undefined) {
      return '#aaa';
    } else if (isRunning ===  0) {
      return '#d9534f';
    } else {
      return '#1cd2a0';
    }
  }
  
  statusText(isRunning) {
    if (isRunning === undefined) {
      return 'N/A';
    } else if (isRunning ===  0) {
      return 'OFF';
    } else {
      return 'ON';
    }
  }

  progressColor(speedFeedback) {
    if (speedFeedback === undefined) {
      return '#aaa';
    } else if (speedFeedback === 0) {
      return '#d9534f';
    } else {
      return 'primary';
    }
  }

  progressBackgroundColor(speedFeedback) {
    if (speedFeedback === undefined) {
      return 'rgb(227, 229, 232);';
    } else if (speedFeedback === 0) {
      return 'rgb(217 83 79 / 57%)';
    } else {
      return 'rgb(167, 202, 237)';
    }
  }

  render() {
    const { title, speedDemanded, speedFeedback, isRunning, pressure, displayPressure, color } = this.props;

    return (
      <Card>
        <CardContent>
          <Stack
            alignItems="flex-start"
            direction="row"
            justifyContent="space-between"
            spacing={3}
          >
            <Stack spacing={1}>
              <Typography
                color="text.secondary"
                gutterBottom
                variant="overline"
              >
                { title }
              </Typography>
              <Typography variant="h4">
                { speedFeedback } %
              </Typography>
            </Stack>
            <div className="hardware_feedback__chip" style={{ backgroundColor: this.backgroundColor(isRunning)}}>
              { this.statusText(isRunning) }
            </div>
          </Stack>
          <Box sx={{ mt: 1 }}>
            <LinearProgress
              value={Math.max(0, Math.min(100, Math.round( (speedFeedback / speedDemanded) * 100)))}
              variant="determinate"
              sx={{
                backgroundColor: this.progressBackgroundColor(speedFeedback),
                '& .MuiLinearProgress-bar': {
                  backgroundColor: this.progressColor(speedFeedback)
                }
              }}
            />
          </Box>

          <div className="hardware_feedback__stats">
            <Box sx={{ pt: 0.5 }}>
              <Typography variant="caption" color="textSecondary">
                Speed demanded: {' '}
                <Typography component="span" variant="caption" sx={{ color: `${color || 'primary'}.main` }}>
                  {speedDemanded}%
                </Typography>{' '}
              </Typography>
            </Box>
            { displayPressure && ( 
              <Box sx={{ pt: 0.5 }}>
                <Typography variant="caption" color="textSecondary">
                  Pressure: {' '}
                  <Typography component="span" variant="caption" sx={{ color: `${color || 'primary'}.main` }}>
                    {pressure}psi
                  </Typography>{' '}
                </Typography>
              </Box>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

}

HardwareFeedback.propTypes = {
  title: PropTypes.string,
  isRunning: PropTypes.bool,
  speedFeedback: PropTypes.number,
  speedDemanded: PropTypes.number,
  pressure: PropTypes.number,
  displayPressure: PropTypes.bool,
  sx: PropTypes.object,
  color: PropTypes.string
};

HardwareFeedback.defaultProps = {
  color: 'primary',
  displayPressure: false
};