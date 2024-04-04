import PropTypes from 'prop-types';
import SpeedIcon from '@mui/icons-material/Speed';
import {
  Avatar,
  Box,
  Card,
  CardContent,
  LinearProgress,
  Stack,
  SvgIcon,
  Typography
} from '@mui/material';

export const AutomationFeedRate = (props) => {
  const { feedRate, feedRateSet, sx, color } = props;

  return (
    <Card sx={sx}>
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
              Feed Rate
            </Typography>
            <Typography variant="h4">
              {feedRate.toFixed(0)} kg/m
            </Typography>
          </Stack>
          <Avatar
            sx={{
              backgroundColor: `${color || 'primary'}.main`,
              height: 56,
              width: 56
            }}
          >
            <SvgIcon>
              <SpeedIcon />
            </SvgIcon>
          </Avatar>
        </Stack>
        <Box sx={{ mt: 1 }}>
          <LinearProgress
            value={Math.max(0, Math.min(100, Math.round( (feedRate / feedRateSet) * 100)))}
            variant="determinate"
            color={color}
          />
        </Box>


        <Box sx={{ pt: 1 }}>
          <Typography variant="caption" color="textSecondary">
            Desired feed rate is {' '}
            <Typography component="span" variant="caption" sx={{ color: `${color || 'primary'}.main` }}>
              {feedRateSet}kg/m
            </Typography>{' '}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

AutomationFeedRate.propTypes = {
  feedRate: PropTypes.number.isRequired,
  feedRateSet: PropTypes.number.isRequired,
  sx: PropTypes.object,
  color: PropTypes.string
};

AutomationFeedRate.defaultProps = {
  color: 'primary'
};