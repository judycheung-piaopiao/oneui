import { TextField, InputAdornment, IconButton } from '@mui/material';
import { Search, Close } from '@mui/icons-material';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
}

export default function SearchBar({ value, onChange }: SearchBarProps) {
  return (
    <TextField
      fullWidth
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="Search tools by name, description, or what you want to do..."
      variant="outlined"
      InputProps={{
        startAdornment: (
          <InputAdornment position="start">
            <Search sx={{ color: '#00d4ff' }} />
          </InputAdornment>
        ),
        endAdornment: value && (
          <InputAdornment position="end">
            <IconButton
              size="small"
              onClick={() => onChange('')}
              sx={{
                color: 'rgba(160, 174, 192, 0.7)',
                '&:hover': {
                  color: '#00d4ff',
                  backgroundColor: 'rgba(0, 212, 255, 0.1)',
                },
              }}
            >
              <Close fontSize="small" />
            </IconButton>
          </InputAdornment>
        ),
      }}
      sx={{
        '& .MuiOutlinedInput-root': {
          borderRadius: 3,
          backgroundColor: 'rgba(26, 31, 58, 0.6)',
          backdropFilter: 'blur(10px)',
          transition: 'all 0.3s ease',
          '& fieldset': {
            borderColor: 'rgba(0, 212, 255, 0.3)',
          },
          '&:hover fieldset': {
            borderColor: 'rgba(0, 212, 255, 0.5)',
          },
          '&.Mui-focused fieldset': {
            borderColor: '#00d4ff',
            boxShadow: '0 0 20px rgba(0, 212, 255, 0.3)',
          },
        },
        '& .MuiInputBase-input': {
          '&:-webkit-autofill': {
            WebkitBoxShadow: '0 0 0 100px rgba(26, 31, 58, 0.6) inset !important',
            WebkitTextFillColor: '#ffffff !important',
            transition: 'background-color 5000s ease-in-out 0s',
          },
        },
        '& .MuiInputBase-input::placeholder': {
          color: 'rgba(160, 174, 192, 0.7)',
          opacity: 1,
        },
      }}
    />
  );
}
