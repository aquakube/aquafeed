import PropTypes from 'prop-types';
import RestaurantIcon from '@mui/icons-material/Restaurant';
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

export const AutomationFeedProgress = (props) => {
  const { percentage, feedDelivered, feedLimit, sx, color, title } = props;

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
              {title}
            </Typography>
            <Typography variant="h4">
              {feedDelivered.toFixed(2)} kg
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
              <RestaurantIcon />
            </SvgIcon>
          </Avatar>
        </Stack>
        <Box sx={{ mt: 1 }}>
          <LinearProgress
            value={Math.max(0, Math.min(100, percentage))}
            variant="determinate"
            color={color}
          />
        </Box>

      <Box sx={{ pt: 1 }}>
        <Typography variant="caption" color="textSecondary">
          Delivered {' '}
          <Typography component="span" variant="caption" sx={{ color: `${color || 'primary'}.main` }}>
            {feedDelivered.toFixed(2)}kg
          </Typography>{' '}
          of {' '}
          <Typography component="span" variant="caption" sx={{ color: `${color || 'primary'}.main` }}>
            {feedLimit}kg
          </Typography>{' '}
        </Typography>
      </Box>

      </CardContent>
    </Card>
  );
};

AutomationFeedProgress.propTypes = {
  title: PropTypes.string.isRequired,
  percentage: PropTypes.number.isRequired,
  feedDelivered: PropTypes.number,
  feedLimit: PropTypes.number,
  sx: PropTypes.object,
  color: PropTypes.string
};

AutomationFeedProgress.defaultProps = {
  title: 'Feed Progress',
  color: 'warning'
};