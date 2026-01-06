import { useState, useEffect } from 'react';
import { Pencil, Trash2, Plus, ArrowLeft } from 'lucide-react';
import type { Tool } from '../types';
import { getTools, deleteTool } from '../api/tools';
import ToolFormModal from './ToolFormModal';

interface AdminPageProps {
  onBack: () => void;
}

export default function AdminPage({ onBack }: AdminPageProps) {
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTool, setEditingTool] = useState<Tool | null>(null);

  useEffect(() => {
    loadTools();
  }, []);

  const loadTools = async () => {
    try {
      setLoading(true);
      const data = await getTools();
      setTools(data);
    } catch (error) {
      console.error('Failed to load tools:', error);
    } finally {
      setLoading(false);
    }
  };

  const getIconDisplay = (icon?: string, name?: string) => {
    if (!icon) return '🔧';
    if (icon.length <= 2) return icon;
    if (icon.startsWith('http') || icon.startsWith('/')) {
      return <img src={icon} alt={name || 'icon'} className="w-8 h-8 object-contain" />;
    }
    return icon;
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this tool?')) return;

    try {
      await deleteTool(id);
      setTools(tools.filter((t) => t.id !== id));
    } catch (error) {
      console.error('Failed to delete tool:', error);
      alert('Failed to delete tool');
    }
  };

  const handleEdit = (tool: Tool) => {
    setEditingTool(tool);
    setShowModal(true);
  };

  const handleAdd = () => {
    setEditingTool(null);
    setShowModal(true);
  };

  const handleModalClose = () => {
    setShowModal(false);
    setEditingTool(null);
    loadTools();
  };

  // Override global scrollbar styles for admin page
  useEffect(() => {
    document.body.classList.add('admin-page-active');
    return () => {
      document.body.classList.remove('admin-page-active');
    };
  }, []);

  return (
    <>
      <style>{`
        body.admin-page-active ::-webkit-scrollbar {
          width: 8px !important;
          height: 8px !important;
        }
        
        body.admin-page-active ::-webkit-scrollbar-track {
          background: #f1f5f9 !important;
        }
        
        body.admin-page-active ::-webkit-scrollbar-thumb {
          background: #cbd5e1 !important;
          border-radius: 4px !important;
        }
        
        body.admin-page-active ::-webkit-scrollbar-thumb:hover {
          background: #94a3b8 !important;
          box-shadow: none !important;
        }
      `}</style>
      <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={onBack}
                className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft size={20} />
                Back to Catalogue
              </button>
              <div className="h-6 w-px bg-gray-300"></div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>
            </div>
            <button
              onClick={handleAdd}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus size={20} />
              Add Tool
            </button>
          </div>
        </div>
      </header>

      {/* Tools Table */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow overflow-x-auto">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/5">
                    Tool
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-2/5">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/6">
                    Tags
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/6">
                    Links
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider w-32">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {tools.map((tool) => (
                  <tr key={tool.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="text-2xl mr-3 flex items-center justify-center">
                          {getIconDisplay(tool.icon, tool.name)}
                        </div>
                        <div className="font-medium text-gray-900">{tool.name}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-500 max-w-md truncate">
                        {tool.description}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {tool.tags.slice(0, 3).map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                        {tool.tags.length > 3 && (
                          <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                            +{tool.tags.length - 3}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <a
                        href={tool.tool_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 mr-3"
                      >
                        Tool
                      </a>
                      {tool.documentation_link && (
                        <a
                          href={tool.documentation_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800"
                        >
                          Docs
                        </a>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => handleEdit(tool)}
                          className="p-2 text-blue-600 hover:text-blue-900 hover:bg-blue-50 rounded-lg transition-colors"
                          title="Edit tool"
                        >
                          <Pencil size={18} />
                        </button>
                        <button
                          onClick={() => handleDelete(tool.id)}
                          className="p-2 text-red-600 hover:text-red-900 hover:bg-red-50 rounded-lg transition-colors"
                          title="Delete tool"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <ToolFormModal
          tool={editingTool}
          onClose={handleModalClose}
        />
      )}
      </div>
    </>
  );
}
