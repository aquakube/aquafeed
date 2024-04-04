import PropTypes from 'prop-types';
import TimerIcon from '@mui/icons-material/Timer';
import {
  Avatar,
  Box,
  Card,
  CardContent,
  Stack,
  SvgIcon,
  Typography
} from '@mui/material';

export const AutomationFeedElapsedTime = (props) => {
  const { phaseElapsedTime, startTime, endTime, sx, color } = props;

  // Convert seconds to minutes
  const elapsedTimeMinutes = (phaseElapsedTime / 60).toFixed(2);

  return (
    <Card sx={sx}>
      <CardContent>
        <Stack
          alignItems="flex-start"
          direction="row"
          justifyContent="space-between"
          // spacing={3}
        >
          <Stack spacing={1}>
            <Typography
              color="text.secondary"
              gutterBottom
              variant="overline"
            >
              Elapsed Time
            </Typography>
            <Typography variant="h4">
              {elapsedTimeMinutes} min
            </Typography>
          </Stack>
          <Avatar
            sx={{
              backgroundColor: 'primary.main',
              height: 56,
              width: 56
            }}
          >
            <SvgIcon>
              <TimerIcon />
            </SvgIcon>
          </Avatar>
        </Stack>
        
        <Box sx={{ pt: 1 }}>
          <Typography variant="caption" color="textSecondary">
            Start time: {' '}
            <Typography component="span" variant="caption" sx={{ color: `${color || 'primary'}.main` }}>
              {startTime}
            </Typography>{' '}
          </Typography>
        </Box>
        { endTime && (
          <Typography variant="caption" color="textSecondary">
            End time: {' '}
            <Typography component="span" variant="caption" sx={{ color: `${color || 'primary'}.main` }}>
              {endTime}
            </Typography>{' '}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
};

AutomationFeedElapsedTime.propTypes = {
  phaseElapsedTime: PropTypes.number.isRequired,
  startTime: PropTypes.string.isRequired,
  endTime: PropTypes.string,
  sx: PropTypes.object,
  color: PropTypes.string
};

AutomationFeedElapsedTime.defaultProps = {
  color: 'primary'
};
