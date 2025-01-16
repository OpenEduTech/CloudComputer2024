// 导入 selenium-webdriver
const { Builder, By, until } = require('selenium-webdriver');
// 导入 chromedriver（确保已安装）
require('chromedriver');

async function runCrawler() {
  // 创建 WebDriver 实例
  let driver = new Builder().forBrowser('chrome').build();

  try {
    // 打开网页
    await driver.get('https://www.baidu.com');

    // 等待页面加载并检查标题
    await driver.wait(until.titleIs('百度一下，你就知道'), 10000);

    // 获取页面标题
    let title = await driver.getTitle();
    console.log('Page Title:', title);

  } catch (error) {
    console.error('Error during crawling:', error);
  } finally {
    // 关闭浏览器
    await driver.quit();
  }
}

runCrawler()

// 导出爬虫函数，供测试或其他文件使用
module.exports = { runCrawler };
