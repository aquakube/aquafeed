import PropTypes from 'prop-types';
import ListIcon from '@mui/icons-material/List';
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

export const PhaseProgress = (props) => {
  const { percentage, phase, phaseDescription, sx } = props;

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
              {phase} Progress
            </Typography>
            <Typography variant="h4">
              {percentage.toFixed(0)}%
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
              <ListIcon />
            </SvgIcon>
          </Avatar>
        </Stack>
        <Box sx={{ mt: 1 }}>
          <LinearProgress
            value={percentage}
            variant="determinate"
          />
          <p className="phase_description">{phaseDescription}</p>
        </Box>
      </CardContent>
    </Card>
  );
};

PhaseProgress.propTypes = {
  phase: PropTypes.string.isRequired,
  phaseDescription: PropTypes.string.isRequired,
  percentage: PropTypes.number.isRequired,
  sx: PropTypes.object
};