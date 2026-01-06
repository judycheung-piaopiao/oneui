import { 
  FormControl, 
  Select, 
  MenuItem, 
  Chip, 
  Box,
  OutlinedInput,
  Checkbox,
  ListItemText,
} from '@mui/material';

interface FilterSidebarProps {
  tags: string[];
  selectedTags: string[];
  onTagToggle: (tag: string) => void;
}

export default function FilterSidebar({ tags, selectedTags, onTagToggle }: FilterSidebarProps) {
  const handleChange = (event: any) => {
    const value = event.target.value;
    const newTags = typeof value === 'string' ? value.split(',') : value;
    
    // Find which tag was added or removed
    const added = newTags.find(tag => !selectedTags.includes(tag));
    const removed = selectedTags.find(tag => !newTags.includes(tag));
    
    if (added) {
      onTagToggle(added);
    } else if (removed) {
      onTagToggle(removed);
    }
  };

  return (
    <FormControl 
      fullWidth
      sx={{
        '& .MuiOutlinedInput-root': {
          borderRadius: 3,
          backgroundColor: 'rgba(10, 14, 39, 0.8)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(0, 212, 255, 0.2)',
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
      }}
    >
      <Select
        multiple
        value={selectedTags}
        onChange={handleChange}
        input={<OutlinedInput />}
        displayEmpty
        renderValue={(selected) => {
          if (selected.length === 0) {
            return <Box sx={{ color: 'rgba(160, 174, 192, 0.7)' }}>Filter by Tags</Box>;
          }
          return <Box sx={{ color: '#00d4ff' }}>{selected.length} tag{selected.length > 1 ? 's' : ''} selected</Box>;
        }}
        MenuProps={{
          PaperProps: {
            sx: {
              backgroundColor: 'rgba(10, 14, 39, 0.95)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(0, 212, 255, 0.2)',
              maxHeight: 400,
              '& .MuiMenuItem-root': {
                transition: 'all 0.2s ease',
                '&:hover': {
                  backgroundColor: 'rgba(0, 212, 255, 0.1)',
                },
                '&.Mui-selected': {
                  backgroundColor: 'rgba(0, 212, 255, 0.2)',
                  '&:hover': {
                    backgroundColor: 'rgba(0, 212, 255, 0.25)',
                  },
                },
              },
            },
          },
        }}
      >
        {tags.map((tag) => (
          <MenuItem 
            key={tag} 
            value={tag}
            sx={{
              textTransform: 'capitalize',
              fontWeight: selectedTags.includes(tag) ? 600 : 400,
              color: selectedTags.includes(tag) ? '#00d4ff' : 'text.primary',
            }}
          >
            <Checkbox 
              checked={selectedTags.includes(tag)}
              sx={{
                color: 'rgba(0, 212, 255, 0.5)',
                '&.Mui-checked': {
                  color: '#00d4ff',
                },
              }}
            />
            <ListItemText primary={tag} />
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}
