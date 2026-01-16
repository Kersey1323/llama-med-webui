import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const navigate = useNavigate();

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  // 控制导航栏的显示/隐藏
  useEffect(() => {
    let timeoutId;

    const handleScroll = () => {
      // 清除之前的定时器
      if (timeoutId) {
        clearTimeout(timeoutId);
      }

      // 设置新的定时器
      timeoutId = setTimeout(() => {
        const currentScrollY = window.scrollY;
        
        // 向下滚动且超过一定距离时隐藏
        if (currentScrollY > lastScrollY && currentScrollY > 100) {
          setIsVisible(false);
        } else {
          setIsVisible(true);
        }
        
        setLastScrollY(currentScrollY);
      }, 100); // 添加100ms的防抖
    };

    window.addEventListener('scroll', handleScroll);
    
    // 清理函数
    return () => {
      window.removeEventListener('scroll', handleScroll);
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [lastScrollY]);

  // 点击导航链接时关闭菜单
  const handleNavClick = () => {
    setIsMenuOpen(false);
  };

  return (
    <>
      <nav className={`navbar ${isVisible ? 'visible' : 'hidden'}`}>
        <div className="container navbar-container">
          <Link to="/" className="navbar-brand" onClick={handleNavClick}>
            LlamaMed
          </Link>

          {/* 移动端菜单按钮 */}
          <button className="menu-toggle" onClick={toggleMenu}>
            <span className={`hamburger ${isMenuOpen ? 'active' : ''}`}></span>
          </button>

          {/* 导航菜单 */}
          <div className={`navbar-menu ${isMenuOpen ? 'active' : ''}`}>
            <Link to="/med-llm" className="nav-link" onClick={handleNavClick}>MedLLM</Link>
            <Link to="/corrector" className="nav-link" onClick={handleNavClick}>Corrector</Link>
            <Link to="/batch-process" className="nav-link" onClick={handleNavClick}>Batch Process</Link>
            <Link to="/profile" className="nav-link" onClick={handleNavClick}>Profile</Link>
          </div>
        </div>
      </nav>

      {/* 添加一个浮动按钮，当导航栏隐藏时显示 */}
      <button 
        className={`navbar-toggle ${!isVisible ? 'visible' : ''}`}
        onClick={() => setIsVisible(true)}
      >
        ↑
      </button>
    </>
  );
};

export default Navbar; 