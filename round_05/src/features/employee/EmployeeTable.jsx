import React, { useState, useEffect, useRef } from 'react';
import api from '../../services/api';

const EmployeeTable = () => {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Pagination & Search state
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const limit = 10;

  // Image upload — use ref so onChange closure always reads the latest id
  const fileInputRef = useRef(null);
  const uploadingIdRef = useRef(null);
  const [uploadingId, setUploadingId] = useState(null); // only for UI spinner

  const handleImageClick = (id) => {
    uploadingIdRef.current = id;   // set ref immediately (synchronous)
    setUploadingId(id);            // also set state to show spinner in UI
    fileInputRef.current.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    const empId = uploadingIdRef.current;  // always fresh — reads from ref, not state

    if (!file || !empId) return;

    // Validate type & size (max 2MB)
    if (!file.type.startsWith('image/')) {
      alert('Please select a valid image file.');
      e.target.value = '';
      return;
    }
    if (file.size > 2 * 1024 * 1024) {
      alert('Image must be smaller than 2MB.');
      e.target.value = '';
      return;
    }

    const reader = new FileReader();
    reader.onload = async (readerEvent) => {
      const base64 = readerEvent.target.result; // data:image/...;base64,...
      try {
        const res = await api.post(`/employees/${empId}/upload-image`, { image: base64 });
        // Update the employee in state immediately
        setEmployees(prev =>
          prev.map(emp =>
            emp.id === empId
              ? { ...emp, profile_image_url: res.data.profile_image_url }
              : emp
          )
        );
      } catch (err) {
        console.error('Upload failed', err);
        alert('Failed to upload image. Please try again.');
      } finally {
        uploadingIdRef.current = null;
        setUploadingId(null);
        e.target.value = ''; // reset so same file can be selected again
      }
    };
    reader.readAsDataURL(file);
  };

  const fetchEmployees = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/employees', {
        params: {
          search: searchTerm,
          page: currentPage,
          limit: limit
        }
      });
      
      const data = response.data.data || response.data;
      setEmployees(Array.isArray(data) ? data : []);
      
      setTotalPages(response.data.total_pages || 1);
    } catch (err) {
      console.error('Failed to fetch employees', err);
      setError('Failed to load employee data. Please try again.');
      
      // For demonstration in boilerplate, we can set mock data if API fails
      setEmployees([
        { id: 1, first_name: 'John', last_name: 'Doe', email: 'john@example.com', role: 'Developer', department: 'Engineering' },
        { id: 2, first_name: 'Jane', last_name: 'Smith', email: 'jane@example.com', role: 'Designer', department: 'Product' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Debounce the search or just trigger on changes
    const delayDebounceFn = setTimeout(() => {
      fetchEmployees();
    }, 500);

    return () => clearTimeout(delayDebounceFn);
  }, [searchTerm, currentPage]);

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this employee?')) {
      try {
        await api.delete(`/employees/${id}`);
        fetchEmployees(); // Refresh list
      } catch (err) {
        console.error('Failed to delete employee', err);
        alert('Failed to delete employee.');
      }
    }
  };

  return (
    <>
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div className="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
        <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Employees</h2>
        
        {/* Search Input */}
        <div className="relative w-full sm:w-64">
          <input
            type="text"
            placeholder="Search employees..."
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1); // Reset to page 1 on new search
            }}
          />
          <span className="absolute left-3 top-2.5 text-gray-400">🔍</span>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
          {error}
        </div>
      )}

      {/* Table Wrapper for horizontal scroll on mobile */}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Avatar
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Name
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Email
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Department
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {loading ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                  Loading...
                </td>
              </tr>
            ) : employees.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                  No employees found.
                </td>
              </tr>
            ) : (
              employees.map((emp) => (
                <tr key={emp.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex-shrink-0 h-10 w-10">
                      <div 
                        onClick={() => handleImageClick(emp.id)}
                        className="h-10 w-10 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center cursor-pointer overflow-hidden border-2 border-transparent hover:border-blue-400 transition-all group relative"
                        title="Click to upload photo"
                      >
                        {uploadingId === emp.id ? (
                          <span className="text-xs text-blue-500 animate-pulse">⏳</span>
                        ) : emp.profile_image_url ? (
                          <>
                            <img src={emp.profile_image_url} alt="" className="h-full w-full object-cover" />
                            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 flex items-center justify-center transition-all">
                              <span className="text-white text-xs opacity-0 group-hover:opacity-100">✏️</span>
                            </div>
                          </>
                        ) : (
                          <span className="text-gray-500 dark:text-gray-300 text-sm group-hover:scale-110 transition-transform">📸</span>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {emp.first_name} {emp.last_name}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">{emp.role}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 dark:text-gray-300">{emp.email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                      {emp.department || 'N/A'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                    <button className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">
                      Edit
                    </button>
                    <button 
                      onClick={() => handleDelete(emp.id)}
                      className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 dark:border-gray-700 sm:px-6 mt-4">
        <div className="flex flex-1 justify-between sm:hidden">
          <button
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
          >
            Previous
          </button>
          <button
            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
          >
            Next
          </button>
        </div>
        <div className="hidden sm:flex flex-1 items-center justify-between">
          <div>
            <p className="text-sm text-gray-700 dark:text-gray-300">
              Showing page <span className="font-medium">{currentPage}</span> of <span className="font-medium">{totalPages}</span>
            </p>
          </div>
          <div>
            <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 dark:ring-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
              >
                <span className="sr-only">Previous</span>
                <span>←</span>
              </button>
              
              {/* Simple page numbers */}
              {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`relative inline-flex items-center px-4 py-2 text-sm font-semibold ring-1 ring-inset ring-gray-300 dark:ring-gray-600 focus:z-20 focus:outline-offset-0 ${
                    page === currentPage 
                    ? 'z-10 bg-blue-600 text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600' 
                    : 'text-gray-900 dark:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  {page}
                </button>
              ))}

              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 dark:ring-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
              >
                <span className="sr-only">Next</span>
                <span>→</span>
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>

      {/* Hidden file input for image upload */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleFileChange}
      />
    </>
  );
};

export default EmployeeTable;
